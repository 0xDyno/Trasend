import time
from decimal import Decimal

from eth_typing import ChecksumAddress
from web3.exceptions import BadFunctionCallOutput, ABIFunctionNotFound
from eth_defi.token import fetch_erc20_details

from src.classes import *
from src import threads, assist, manager

"""
Helps Manager to work with transactions
trans >>> transactions

Use send_ to send ETH
Use send_
"""


def print_gas_price_info():
    """Prints info about current gas"""
    if manager.Manager.gas_price is None or manager.Manager.max_priority is None:
        print(f"No info yet, try again... now. It updates every {settings.update_gas_every} secs")
        return
    gas = Web3.fromWei(manager.Manager.gas_price, "gwei")
    priority = Web3.fromWei(manager.Manager.max_priority, "gwei")
    network_gas = Web3.fromWei(manager.Manager.network_gas_price, "gwei")
    network_priority = Web3.fromWei(manager.Manager.network_max_priority, "gwei")

    current_gas = "Current state: gas = {:.02f} gwei, priority = {} gwei (live {:.2f}, {:.2f}) | " \
        "settings: min gas = {} <> min prior = {}".format(gas, priority, network_gas, network_priority,
                                                          settings.min_gas_price, settings.min_priority)

    print(current_gas)


def get_max_fee(gas: int):
    return (manager.Manager.gas_price + manager.Manager.max_priority) * gas


def print_price_and_confirm_native(chain_id, value, receivers: int) -> bool:
    """Prints the price for the transaction and ask to confirm before sending """
    if receivers > 1:
        tr = "transactions"
    else:
        tr = "transaction"
    coin = settings.chain_default_coin[chain_id]
    base_fee = (manager.Manager.network_gas_price + manager.Manager.max_priority) * settings.gas_native
    max_fee = (manager.Manager.gas_price + manager.Manager.max_priority) * settings.gas_native
    total_send = Web3.fromWei(value * receivers, "ether")

    base_fee = Web3.fromWei(base_fee * receivers, "ether")
    max_fee = Web3.fromWei(max_fee * receivers, "ether")

    total_base = base_fee + total_send
    total_max = max_fee + total_send
    ask = f"\nFor {receivers} {tr}. Amount: {total_send:.3f} {coin}\n" \
          f"Base Fee: {base_fee:.4f} {coin} | Max Fee: {max_fee:.4f} {coin}\n" \
          f"Total: {total_base:.4f} {coin} (max {total_max:.4f} {coin})\n"
    return assist.confirm(print_before=ask)


def print_price_and_confirm_erc20(token: Token, erc20, sender, receivers: int, amount) -> bool:
    symb = token.symbol
    coin = settings.chain_default_coin[token.chain_id]
    if receivers > 1:
        tr = "transactions"
    else:
        tr = "transaction"

    try:		# Count Base & Max fee from Estimated gas * multiplier
        data = {"from": sender.addr}
        gas = int(erc20.functions.transfer(sender.addr, amount).estimateGas(data) * settings.multiply_gas)
        base_fee = (manager.Manager.network_gas_price + manager.Manager.max_priority) * gas
        max_fee = (manager.Manager.gas_price + manager.Manager.max_priority) * gas
    except Exception as e:		# If we can't do it by some reason - use default settings
        print("Failed to get live gas required, use the settings. Error:", e)
        base_fee = (manager.Manager.network_gas_price + manager.Manager.max_priority) * settings.average_gas_erc20
        max_fee = (manager.Manager.gas_price + manager.Manager.max_priority) * settings.gas_erc20

    amount = convert_to_normal_view(amount, token.decimal)
    total_send = amount * receivers

    total_fee_base = Web3.fromWei(base_fee * receivers, "ether")
    total_fee_max = Web3.fromWei(max_fee * receivers, "ether")

    ask = f"\nFor {receivers} {tr}. Tokens: {total_send:.2f} {symb}\n" \
          f"Base Fee: {total_fee_base:.4f} {coin} | Max Can Be Used: {total_fee_max:.4f} {coin}\n"
    return assist.confirm(print_before=ask)


def convert_to_normal_view(not_normal: int, decimal) -> Decimal:
    """Use to convert 1000000000000000000 Wei to 1 ETH"""
    return Decimal(not_normal) / Decimal(10 ** decimal)


def convert_for_machine(normal: Decimal, decimal) -> int:
    """Use to convert 1 ETH to 1000000000000000000 Wei"""
    return int(normal * 10 ** decimal)


def convert_to_normal_view_str(decimal, not_normal=1) -> str:
    min_ = convert_to_normal_view(not_normal, decimal)
    str_format = "{0:." + decimal.__str__() + "f}"
    return str_format.format(min_)


def get_list_with_str_addresses(wallets: list):
    """Receives list with Wallets or str-Addresses and convert it to str-Addresses"""
    new_list = wallets.copy()					# make copy
    for i in range(len(new_list)):
        if isinstance(new_list[i], Wallet):		# if element is Wallet
            new_list[i] = new_list[i].addr		# change it with it's addr
    return new_list


def send_erc20_or(w3: Web3) -> bool | ChecksumAddress:
    """Returns what to send - Native or ERC-20
    If Native - False, If Contract - ChecksumAddress"""
    coin = settings.chain_default_coin[w3.eth.chain_id]
    what_to_send = input(texts.what_to_send.format(coin)).strip()
    if not what_to_send:  # so, that's main
        return False									# if empty - then it's native coin

    try:
        what_to_send = w3.toChecksumAddress(what_to_send)		# check it's address
        if w3.eth.get_code(what_to_send):   # True - if contract, False - if address
            return what_to_send									# return address
    except (TypeError, ValueError):
        pass
    print(texts.error_not_contract_address)  # Otherwise that's wrong input
    raise InterruptedError(texts.exited)


def get_amount_for_erc20(erc20, token: Token, sender: Wallet, receivers: int) -> int:
    """
    Checks balance and ask how much to send to each
    :return: amount to send (if 0.01 and dec 6 -> that's 1000)
    """
    balance_raw = erc20.functions.balanceOf(sender.addr).call()				# check balance and print it
    balance = Decimal(convert_to_normal_view(balance_raw, token.decimal))
    print("> Balance is >> {:.2f}".format(balance))
    print("> Minimum for", token.symbol, "is", convert_to_normal_view_str(token.decimal))
    wish_send = input("How much you want to send to each? >> ").strip().lower()	# ask to write amount to send

    assist.check_balances(balance, wish_send, receivers)
    return convert_for_machine(Decimal(wish_send), token.decimal)


def get_amount_for_native(w3: Web3, sender: Wallet, receivers: list) -> int:
    native_coin = settings.chain_default_coin[w3.eth.chain_id]
    text_in_input = "How much you want send to each? >> "
    balance = sender.get_eth_balance()
    
    print("> Balance is >> {:.2f} {}".format(balance, native_coin))
    amount_to_send = assist.print_ask(text_in_input=text_in_input)
    assist.check_balances(balance, amount_to_send, len(receivers))
    
    return Web3.toWei(amount_to_send, "ether")


# SENDING NATIVE COIN


def sender_native(w3: Web3, sender: Wallet, receivers: list, value) -> list:
    """
    Sends asset from 1 wallet to N others wallets chosen amount.
    If Amount = 2 and 20 receivers, then will be sent 2*20 = 40 units
    """
    txs = list()
    receivers_str = get_list_with_str_addresses(receivers)
    nonce = sender.nonce
    chain_id = w3.eth.chain_id
    amount = str(convert_to_normal_view(value, 18))

    for i in range(len(receivers_str)):
        if len(receivers_str) > 1:
            assist.create_progress_bar(i, len(receivers_str))
        tx_hash = _send_native(w3, chain_id, sender, nonce + i, receivers_str[i], value)

        txs.append(Transaction(chain_id, time.time(), receivers[i], sender, amount, tx_hash))

    threads.start_todo(update_txs, True, w3, txs)
    return txs


def _send_native(w3: Web3, chain_id: int, sender: Wallet, nonce, receiver: Wallet, value) -> str:
    """
    Tries to send transaction with the last ETH updates. But it won't work for networks that didn't update
    So I wrote also second variant to send transaction, that happens when we receive an error
    :return: transaction hash, string
    """
    try:
        tx = {
            "from": sender.addr,
            "to": receiver,
            "gas": 21000,
            "maxFeePerGas": manager.Manager.gas_price,
            "maxPriorityFeePerGas": manager.Manager.max_priority,
            "value": value,
            "data": b'',
            "nonce": nonce,
            "type": 2,
            "chainId": chain_id
        }
        signed_tx = w3.eth.account.sign_transaction(tx, sender.key())
        tx_hash_hexbytes = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return w3.toHex(tx_hash_hexbytes)
    except Exception:		# Some BlockChains doesn't work with TX type 2, so here I try to use old way
        tx = {
            "to": receiver,
            "nonce": sender.nonce,
            "gas": 21000,
            "gasPrice": manager.Manager.gas_price,
            "value": value,
            "chainId": chain_id
        }
        signed_tx = w3.eth.account.sign_transaction(tx, sender.key())
        tx_hash_hexbytes = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return w3.toHex(tx_hash_hexbytes)


# SENDING ERC - 20 TOKENS


def update_erc_20(w3: Web3, sc_addr):
    """
    If the Token exists - return it. If not - connect, save & return
    :return: Token obj
    """
    """If we don't have that contrat in the system - do connection, get info and save new Token to the system"""
    if assist.is_contract_exist(w3.eth.chain_id, sc_addr):
        return assist.get_token(w3, sc_addr)
    
    try:
        erc20 = w3.eth.contract(address=sc_addr, abi=settings.ABI)		# get erc20 connection
        symbol = erc20.functions.symbol().call()						# get symbol
        decimal = erc20.functions.decimals().call()						# get decimal and add
        abi = settings.ABI
    except (BadFunctionCallOutput, ABIFunctionNotFound):		        # Longer + Not So Safe
        erc20 = fetch_erc20_details(w3, sc_addr)				        # get connection and add the token
        symbol = erc20.symbol
        decimal = erc20.decimals
        abi = erc20.contract.abi
    return assist.add_smart_contract_token(w3.eth.chain_id, sc_addr,
                                                symbol, decimal, abi)



def sender_erc20(erc20, token: Token, sender: Wallet, receivers: list, amount) -> list:
    """Receive list with receivers as Wallets, but work as str-address. That made for purpose to send TXs not
    only to Wallets in the system. But for TXs creation give Wallets, to add TXs to the list if it's Wallet obj"""
    txs = list()
    receivers_str = get_list_with_str_addresses(receivers)
    nonce = sender.nonce
    chain_id = erc20.web3.eth.chain_id
    save_amount = str(convert_to_normal_view(amount, token.decimal))

    for i in range(len(receivers_str)):
        if len(receivers_str) > 1:
            assist.create_progress_bar(i, len(receivers_str))
        tx_hash = _send_erc20(erc20, sender.addr, sender.key(), nonce + i, receivers_str[i], amount)
        tx = Transaction(chain_id, time.time(), receivers[i], sender, save_amount, tx_hash, token.symbol, token.sc_addr)
        txs.append(tx)

    threads.start_todo(update_txs, True, erc20.web3, txs)
    return txs


def _send_erc20(erc20, sender: str, sender_key: str, nonce, receiver: str, amount):
    tx_dict = {
        "from": sender,
        "chainId": erc20.web3.eth.chain_id,
        "nonce": nonce,
        "maxFeePerGas": manager.Manager.gas_price,
        "maxPriorityFeePerGas": manager.Manager.max_priority,
        "type": 2,
        "gas": settings.gas_erc20,
    }
    raw_tx = erc20.functions.transfer(receiver, amount).build_transaction(tx_dict)
    signed = erc20.web3.eth.account.sign_transaction(raw_tx, sender_key)
    tx_hash = erc20.web3.eth.send_raw_transaction(signed.rawTransaction)
    return Web3.toHex(tx_hash)  # return TX


def update_txs(w3: Web3, txs_list: list):
    for tx in txs_list:											# for all txs
        if threads.can_create_daemon():							# if we can create daemon
            threads.start_todo(update_tx, True, w3, tx)			# create to do update_tx()
        else:
            time.sleep(settings.wait_to_create_daemon_again)	# or wait


def update_tx(w3: Web3, tx: Transaction):
    if tx.status is None:										# if no status
        receipt = w3.eth.wait_for_transaction_receipt(tx.tx)  	# wait for the result
        if receipt["status"] == 0:								# and change it
            tx.status = "Fail"
        else:
            tx.status = "Success"