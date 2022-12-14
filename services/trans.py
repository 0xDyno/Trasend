import time
from decimal import Decimal

from web3.exceptions import BadFunctionCallOutput, ABIFunctionNotFound
from services.classes import *
from services import threads, logs, assist, manager
from eth_defi.token import fetch_erc20_details

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
	network_gas = float(Web3.fromWei(manager.Manager.network_gas_price, "gwei")) / settings.gas_multiplier
	network_priority = float(Web3.fromWei(manager.Manager.network_max_priority, "gwei")) / settings.priority_multiplier

	current_gas = "Current state: gas = {:.02f} gwei, priority = {} gwei (live {:.2f}, {:.2f}) | " \
		"settings: min gas = {} <> min prior = {}".format(gas, priority, network_gas, network_priority,
																	 settings.min_gas, settings.min_priority)

	print(current_gas)


def print_price_and_confirm(chain_id, value, receivers: list | set | tuple) -> bool:
	"""Prints the price for the transaction and ask to confirm before sending """
	coin = settings.chain_default_coin[chain_id]
	tx_number = len(receivers)					# get No of TXs will be made
	gas_price = manager.Manager.gas_price		# get gas price (like gwei, but in wei | 1gwei=1000000000wei)
	priority = manager.Manager.max_priority
	fee = (gas_price + priority) * 21000

	total_send = value * tx_number
	total_fee = fee * tx_number

	total_send = Web3.fromWei(total_send, "ether")
	total_fee = Web3.fromWei(total_fee, "ether")
	total = total_fee + total_send
	ask = f"Amount: {total_send:.3f} {coin}\n" \
		f"Fee: {total_fee:.3f} {coin}\n" \
	  	f"Total: {total:.3f} {coin}\n"

	return assist.confirm(print_before=ask)


def get_gas(w3: Web3, receiver: Wallet, last_block) -> int:
	"""
	Return required gas for that transaction
	:return int: required gas (21k for ETH transfer)
	"""
	tx = {
		"to": receiver,
		"value": 1,
		"chainId": w3.eth.chain_id
	}
	return w3.eth.estimate_gas(tx, last_block["number"])


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


def update_erc_20(w3: Web3, sc_addr):
	"""If we don't have that contrat in the system - do connection, get info and save new Token to the system"""
	if not assist.is_contract_exist(w3.eth.chain_id, sc_addr):
		try:
			erc_20 = w3.eth.contract(address=sc_addr, abi=settings.ABI)			# get erc_20 connection
			symbol = erc_20.functions.symbol().call()							# get symbol
			decimal = erc_20.functions.decimals().call()						# get decimal
			assist.add_smart_contract_token(w3.eth.chain_id, sc_addr, symbol, decimal)		# add it
		except (BadFunctionCallOutput, ABIFunctionNotFound):
			erc_20 = fetch_erc20_details(w3, sc_addr)				# get connection and add the token
			assist.add_smart_contract_token(w3.eth.chain_id, sc_addr, erc_20.symbol, erc_20.decimals, erc_20.contract.abi)


def transaction_sender(w3: Web3, sender: Wallet, receivers: list | Wallet, value) -> list:
	"""
	Sends asset from 1 wallet to N others wallets chosen amount.
	If Amount = 2 and 20 receivers, then will be sent 2*20 = 40 units
	:param w3:
	:param sender:
	:param receivers: list with Wallets or Wallet obj
	:param value:
	:return: list with TXs (str)
	"""
	if isinstance(receivers, Wallet):		# if it's Wallet - make list
		receivers = [receivers]				# with 1 Wallet

	txs = list()

	for i in range(len(receivers)):		# for each receiver send transaction
		tx = compose_native_transaction(w3, sender, sender.nonce + i,
										receivers[i], value)
		txs.append(tx)					# add tx

	threads.start_todo(update_txs, True, w3, txs)
	return txs


def transaction_sender_erc20(w3: Web3, erc20, token: Token, sender: Wallet, receivers: list, amount) -> list:
	txs = list()
	nonce = sender.nonce

	for i in range(len(receivers)):
		tx_hash = send_erc20(w3, erc20, sender.addr, sender.key(), nonce+i, receivers[i].addr, amount)
		txs.append(Transaction(w3.eth.chain_id, time.time(), receivers[i], sender,
							   str(convert_to_normal_view(amount, token.decimal)), tx_hash, token.symbol, token.sc_addr))

	threads.start_todo(update_txs, True, w3, txs)
	return txs



def send_erc20(w3: Web3, erc20, sender: str, sender_key: str, nonce, receiver: str, amount):
	tx_dict = {
		"from": sender,
		"chainId": w3.eth.chain_id,
		"nonce": nonce,
		"maxFeePerGas": manager.Manager.gas_price,
		"maxPriorityFeePerGas": manager.Manager.max_priority,
		"type": 2,
		"gas": 215840,
	}
	raw_tx = erc20.functions.transfer(receiver, amount).build_transaction(tx_dict)
	signed = w3.eth.account.sign_transaction(raw_tx, sender_key)
	tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
	return w3.toHex(tx_hash)  # return TX


def compose_native_transaction(w3: Web3, sender: Wallet, nonce, receiver: Wallet, value) -> Transaction:
	"""
	Tries to send transaction with the last ETH updates. But it won't work for networks that didn't update
	So I wrote also second variant to send transaction, that happens when we receive an error
	:return: transaction hash, string
	"""
	chain_id = w3.eth.chain_id

	try:  # Usual way that should work
		logs.pr_trans("compose_transaction_and_send: try to send transaction, type #2")
		tx = {
			"from": sender.addr,
			"to": receiver.addr,
			"gas": 21000,
			"maxFeePerGas": manager.Manager.gas_price,
			"maxPriorityFeePerGas": manager.Manager.max_priority,
			"value": value,
			"data": b'',
			"nonce": nonce,
			"type": 2,
			"chainId": chain_id
		}
		tx_hash = send_native_coin(w3, tx, sender.key())
	except Exception:
		# When something wrong (wrong network etc..) - the last try.. can work because some networks
		# don't have ETH updates and don't support new gas type
		logs.pr_trans("compose_transaction_and_send: Fail")
		logs.pr_trans("compose_transaction_and_send: try to send transaction no-type")
		tx = {
			"to": receiver.addr,
			"nonce": sender.nonce,
			"gas": 21000,
			"gasPrice": manager.Manager.gas_price,
			"value": value,
			"chainId": chain_id
		}
		tx_hash = send_native_coin(w3, tx, sender.key())
	finally:
		logs.pr_trans("compose_transaction_and_send: successfully sent")

	return Transaction(chain_id, time.time(), receiver, sender, str(w3.fromWei(value, "ether")), tx_hash)


def send_native_coin(w3: Web3, tx: dict, key) -> str:
	"""
	Sends transaction when sends only native coins (ETH, BNB etc)
	:param w3: Web3 obj
	:param tx: dict with transaction data
	:param key:
	:return: transaction hash or None if failed
	"""
	logs.pr_trans("send_native_coin: try to send a transaction", end=" ")
	signed_tx = w3.eth.account.sign_transaction(tx, key)				# sing
	tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)	# send
	logs.pr_trans("send_native_coin: successfully sent the transaction")
	return w3.toHex(tx_hash)											# return TX


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