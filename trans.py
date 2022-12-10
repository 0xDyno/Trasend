from decimal import Decimal
from web3 import Web3
from config import settings
from wallet import Wallet

"""
Helps Manager to work with transactions
trans >>> transactions

Use send_ to send ETH
Use send_
"""


def pr(text):
	if settings.print_trans_info:
		print(f"\n---------\n>>>>>>>>>> {text}\n---------\n")


def get_gas(web3: Web3, receiver: Wallet, last_block) -> int:
	"""
	Return required gas for that transaction
	:return int: required gas (21k for ETH transfer)
	"""
	tx = {
		"to": receiver,
		"value": 1,
		"chainId": web3.eth.chain_id
	}
	return web3.eth.estimate_gas(tx, last_block["number"])


def send_transactions(web3: Web3, sender: Wallet, list_with_receivers: list, value) -> list:
	"""
	Sends asset from 1 wallet to N others wallets chosen amount.
	If amount is 2 and 20 receivers, then will be sent 40 units
	:param web3:
	:param sender:
	:param list_with_receivers: list with Wallets or Wallet obj
	:param value:
	:return: list with TXs (str)
	"""
	if isinstance(list_with_receivers, Wallet):			# if it's Wallet - make list
		list_with_receivers = [list_with_receivers]

	list_with_transactions = list()
	length = len(list_with_receivers)
	for i in range(length):											# for each receiver
		tx_hash = send_transaction(web3, sender, sender.nonce + i,	# send TX
								   list_with_receivers[i], value)
		list_with_transactions.append(tx_hash)						# add tx_hash
	return list_with_transactions


def send_transaction(web3: Web3, sender: Wallet, nonce, receiver: Wallet, value) -> str:
	"""
	Tries to send transaction with the last ETH updates. But it won't work for networks that didn't update
	So I wrote also second variant to send transaction
	:return: transaction hash, string
	"""
	max_gas_fee = int(web3.eth.gas_price * settings.multiplier)
	max_prior_fee = int(web3.eth.max_priority_fee * settings.multiplier)

	try:  # Usual way that should work
		pr("compose_transaction_and_send: try to send transaction #1")
		tx = {
			"from": sender.addr,
			"to": receiver.addr,
			"gas": 21000,
			"maxFeePerGas": max_gas_fee,
			"maxPriorityFeePerGas": max_prior_fee,
			"value": web3.toWei(value, "ether"),
			"data": b'',
			"nonce": nonce,
			"type": 2,
			"chainId": web3.eth.chain_id
		}
		return send_native_coin(web3, tx, sender.key())
	except Exception:
		# When something wrong (wrong network etc..) - the last try.. can work because some networks
		# don't have ETH updates and don't support new gas type
		pr("compose_transaction_and_send: try to send transaction #1 - Fail")
		pr("compose_transaction_and_send: try to send transaction #2")
		tx = {
			"to": receiver.addr,
			"nonce": sender.nonce,
			"gas": 21000,
			"gasPrice": int(web3.eth.gas_price * settings.multiplier),
			"value": web3.toWei(value, "ether"),
			"chainId": web3.eth.chain_id
		}
		return send_native_coin(web3, tx, sender.key())
	finally:
		pr("compose_transaction_and_send: successfully transaction")


def send_native_coin(web3: Web3, tx: dict, key) -> str or None:
	"""
	Sends transaction when sends only native coins (ETH, BNB etc)
	:param web3: Web3 obj
	:param tx: dict with transaction data
	:return: transaction hash or None if failed
	"""

	pr("send_native_coin: try to send a transaction")
	signed_tx = web3.eth.account.sign_transaction(tx, key)
	tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
	pr("send_native_coin: successfully sent the transaction")
	return web3.toHex(tx_hash)