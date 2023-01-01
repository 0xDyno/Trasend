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


def print_price_and_confirm_native(chain_id, value, receivers: int) -> bool:
    """Prints the price for the transaction and ask to confirm before sending"""
    def type_one():
        base_fee_wei = manager.Manager.gas_price * settings.gas_native
        base_fee = Web3.fromWei(base_fee_wei * receivers, "ether")
        
        total = base_fee + total_send

        return f"\nFor {receivers} {tr}.\n" \
               f"Amount: {total_send:.3f} {coin}\n" \
               f"Fee: {base_fee:.4f} {coin}\n" \
               f"Total: {total:.4f} {coin}\n"
    
    def type_1_2(use_priority: bool):
        """
        If it's type 3, use_priority should be True
        If it's type 2, use_priority should be False
        """
        priority = manager.Manager.max_priority if use_priority else 0
        
        base_fee_wei = (manager.Manager.network_gas_price + priority) * settings.gas_native
        base_fee = Web3.fromWei(base_fee_wei * receivers, "ether")
        total_average = base_fee + total_send
        
        max_fee_wei = (manager.Manager.gas_price + priority) * settings.gas_native
        max_fee = Web3.fromWei(max_fee_wei * receivers, "ether")
        total_max = max_fee + total_send
        
        return f"\nFor {receivers} {tr}:\n" \
               f"Amount: {total_send:.3f} {coin}\n" \
               f"Base Fee: {base_fee:.4f} {coin} | Max Fee: {max_fee:.4f} {coin}\n" \
               f"Total: {total_average:.4f} {coin} (max {total_max:.4f} {coin})\n"
    
    coin = settings.chain_default_coin[chain_id]
    tr = "transactions" if receivers > 1 else "transaction"
    total_send = Web3.fromWei(value * receivers, "ether")

    match settings.chain_update_type[chain_id]:
        case 1:
            ask = type_one()
        case 2:
            ask = type_1_2(use_priority=False)
        case 3:
            ask = type_1_2(use_priority=True)
        case _:
            ask = "> Error. Can't calculate gas info because update type is not known."
    
    return assist.confirm(print_before=ask)


def print_price_and_confirm_erc20(token: Token, erc20, sender, receivers: int, amount) -> bool:
    def type_1():
        print("TYPE - 1")
        base_fee = manager.Manager.gas_price * gas
        total_fee_base = Web3.fromWei(base_fee * receivers, "ether")
        return f"\nFor {receivers} {tr}:\n" \
               f"Tokens: {total_send:.2f} {symb}\n" \
               f"Fee: {total_fee_base:.4f} {coin}\n"
    
    def type_2_3(use_priority: bool):
        """
        If it's type 3, use_priority should be True
        If it's type 2, use_priority should be False
        """
        print("TYPE 2 - 3")
        priority = manager.Manager.max_priority if use_priority else 0
        
        base_fee = (manager.Manager.network_gas_price + priority) * gas
        max_fee = (manager.Manager.gas_price + priority) * gas_max
    
        total_fee_base = Web3.fromWei(base_fee * receivers, "ether")
        total_fee_max = Web3.fromWei(max_fee * receivers, "ether")
    
        return f"\nFor {receivers} {tr}:\n" \
               f"Tokens: {total_send:.2f} {symb}\n" \
               f"Base Fee: {total_fee_base:.4f} {coin} | Max Can Be Used: {total_fee_max:.4f} {coin}\n"
        
    symb = token.symbol
    coin = settings.chain_default_coin[token.chain_id]
    total_send = convert_to_normal_view(amount, token.decimal) * receivers
    tr = "transactions" if receivers > 1 else "transaction"
    gas = get_native_gas_for_erc20(erc20, sender, amount)
    gas_max = get_max_gas_for_erc20(erc20, sender, amount)

    match settings.chain_update_type[erc20.web3.eth.chain_id]:
        case 1:
            ask = type_1()
        case 2:
            ask = type_2_3(use_priority=False)
        case 3:
            ask = type_2_3(use_priority=True)
        case _:
            ask = "> Error. Can't calculate gas info because update type is not known."

    return assist.confirm(print_before=ask)

    
def get_max_gas_for_erc20(erc20, sender: Wallet, amount):
    return int(get_native_gas_for_erc20(erc20, sender, amount) * settings.multiply_gas)


def get_native_gas_for_erc20(erc20, sender: Wallet, amount):
    """
    Check required gas for transaction and multiply it, because in general web3
    calculates gas wrong for ~10%. So in usual multiply is x1.2. But in case of
    BNB blockchains - it multiplies for 1.7x, because BNBchains return wrong required gas
    
    If it can't calculate  - uses default gas
    """
    multi = 1.7 if erc20.web3.eth.chain_id == 56 or erc20.web3.eth.chain_id == 97 else 1.2
    
    try:
        data = {"from": sender.addr}
        return int(erc20.functions.transfer(sender.addr, amount).estimateGas(data)) * multi
    except Exception as e:
        print("Failed to calculate required gas, will be used from the settings. Error:", e)
        return settings.average_gas_erc20


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
    for i, wallet in enumerate(new_list):
        if isinstance(wallet, Wallet):          # if element is Wallet
            new_list[i] = wallet.addr           # change it with it's addr
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
            
        tx_hash = __send_native(w3, chain_id, sender, nonce + i, receivers_str[i], value)
        txs.append(Transaction(chain_id, time.time(), receivers[i], sender, amount, tx_hash))

    threads.start_todo(update_txs, True, w3, txs)
    return txs


def __send_native(w3: Web3, chain_id: int, sender: Wallet, nonce, receiver: str, value) -> str:
    """
    Send TXs in usual way if priority doesn't support or with new Type 2
    :return: transaction hash, string
    """
    tx = {
        "to": receiver,
        "nonce": nonce,
        "gas": 21000,
        "value": value,
        "chainId": chain_id
    }
    
    if settings.chain_update_type[chain_id] == 3:
        tx["from"] = sender.addr
        tx["maxFeePerGas"] = manager.Manager.gas_price
        tx["maxPriorityFeePerGas"] = manager.Manager.max_priority
        tx["data"] = b''
        tx["type"] = 2
    else:
        tx["gasPrice"] = manager.Manager.gas_price

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
    return assist.add_smart_contract_token(w3.eth.chain_id, sc_addr, symbol, decimal, abi)



def sender_erc20(erc20, token: Token, sender: Wallet, receivers: list, amount) -> list:
    """Receive list with receivers as Wallets, but work as str-address. That made for purpose to send TXs not
    only to Wallets in the system. But for TXs creation give Wallets, to add TXs to the list if it's Wallet obj"""
    txs = list()
    receivers_str = get_list_with_str_addresses(receivers)
    nonce = sender.nonce
    chain_id = erc20.web3.eth.chain_id
    save_amount = str(convert_to_normal_view(amount, token.decimal))
    gas = get_max_gas_for_erc20(erc20, sender, amount)
    
    for i in range(len(receivers_str)):
        if len(receivers_str) > 1:
            assist.create_progress_bar(i, len(receivers_str))
            
        tx_hash = __send_erc20(erc20, chain_id, gas, sender.addr, sender.key(), nonce + i, receivers_str[i], amount)
        tx = Transaction(chain_id, time.time(), receivers[i], sender, save_amount, tx_hash, token.symbol, token.sc_addr)
        txs.append(tx)

    threads.start_todo(update_txs, True, erc20.web3, txs)
    return txs


def __send_erc20(erc20, chain_id: int, gas: int, sender: str, sender_key: str, nonce, receiver: str, amount):
    tx_dict = {
            "from": sender,
            "chainId": chain_id,
            "nonce": nonce,
            "gas": gas,
        }
    
    if settings.chain_update_type[chain_id] == 3:
        tx_dict["type"] = 2
        tx_dict["maxFeePerGas"] = manager.Manager.gas_price
        tx_dict["maxPriorityFeePerGas"] = manager.Manager.max_priority
    else:
        tx_dict["gasPrice"] = manager.Manager.gas_price
        
    
    raw_tx = erc20.functions.transfer(receiver, amount).build_transaction(tx_dict)
    signed = erc20.web3.eth.account.sign_transaction(raw_tx, sender_key)
    tx_hash = erc20.web3.eth.send_raw_transaction(signed.rawTransaction)
    return Web3.toHex(tx_hash)


def update_txs(w3: Web3, txs_list: list):
    for tx in txs_list:											# for all txs
        if threads.can_create_daemon():							# if we can create daemon
            threads.start_todo(update_tx, True, w3, tx)			# create to do update_tx()
        else:
            time.sleep(settings.wait_to_create_daemon_again)	# or wait


def update_tx(w3: Web3, tx: Transaction):
    if tx.chain_id != w3.eth.chain_id:
        return
    
    if tx.status is None:										# if no status
        receipt = w3.eth.wait_for_transaction_receipt(tx.tx)  	# wait for the result
        if receipt["status"] == 0:								# and change it
            tx.status = "Fail"
        else:
            tx.status = "Success"