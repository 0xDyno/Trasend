import time

from config import settings
from services.classes import *
from services import threads, logs, assist, manager

"""
Helps Manager to work with transactions
trans >>> transactions

Use send_ to send ETH
Use send_
"""


def print_price_and_confirm(chain_id, value, receivers: list | set | tuple) -> bool:
	"""Prints the price for the transaction and ask to confirm before sending """
	coin = chain_default_coin[chain_id]
	tx_number = len(receivers)							# get No of TXs will be made
	gas_price = manager.Manager.gas_price				# get gas price (gwei, but in wei)
	priority = manager.Manager.max_priority * settings.multiplier_priority 	# and priority
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
	length = len(receivers)

	for i in range(length):				# for each receiver send transaction
		tx = compose_native_transaction(w3, sender, sender.nonce + i,
										receivers[i], value)
		txs.append(tx)					# add tx

	threads.start_todo(update_txs, True, w3, txs)
	return txs


def compose_native_transaction(w3: Web3, sender: Wallet, nonce, receiver: Wallet, value) -> Transaction:
	"""
	Tries to send transaction with the last ETH updates. But it won't work for networks that didn't update
	So I wrote also second variant to send transaction
	:return: transaction hash, string
	""" 			# no change in
	max_gas_fee = int(manager.Manager.gas_price * settings.multiplier)		# SHOULD BE INT !!! That's wei, so Ok. And
	max_prior_fee = int(manager.Manager.max_priority * settings.multiplier_priority)   # web3 doesn't work with float.
	chain_id = w3.eth.chain_id

	try:  # Usual way that should work
		logs.pr_trans("compose_transaction_and_send: try to send transaction, type #2")
		tx = {
			"from": sender.addr,
			"to": receiver.addr,
			"gas": 21000,
			"maxFeePerGas": max_gas_fee,
			"maxPriorityFeePerGas": max_prior_fee,
			"value": value,
			"data": b'',
			"nonce": nonce,
			"type": 2,
			"chainId": chain_id
		}
		tx_hash = send_native_coin(w3, tx, sender.key())
	except Exception as e:
		# When something wrong (wrong network etc..) - the last try.. can work because some networks
		# don't have ETH updates and don't support new gas type
		logs.pr_trans("compose_transaction_and_send: Fail")
		logs.pr_trans("compose_transaction_and_send: try to send transaction no-type")
		tx = {
			"to": receiver.addr,
			"nonce": sender.nonce,
			"gas": 21000,
			"gasPrice": int(w3.eth.gas_price * settings.multiplier),
			"value": value,
			"chainId": chain_id
		}
		tx_hash = send_native_coin(w3, tx, sender.key())
	finally:
		logs.pr_trans("compose_transaction_and_send: successfully sent")

	return Transaction(chain_id, time.time(), receiver, sender, value, tx_hash)


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
			threads.start_todo(update_tx, True, w3, tx)		# create to do update_tx()
		else:
			time.sleep(settings.wait_to_create_daemon_again)	# or wait


def update_tx(w3: Web3, tx: Transaction):
	if tx.status is None:										# if no status
		receipt = w3.eth.wait_for_transaction_receipt(tx.tx)  # wait for the result
		if receipt["status"] == 0:								# and change it
			tx.status = "Fail"
		else:
			tx.status = "Success"