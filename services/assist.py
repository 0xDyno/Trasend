import time
from eth_account import Account

import services.manager
from config import settings, text
from random import random
from web3 import Web3
from datetime import date
from cryptography.fernet import Fernet
from services.classes import Wallet
from services import threads, trans
import os


"""
File with general methods to alleviate Manager (make it easy to read)
Not important methods/functions which doesn't work with data directly will be here
"""


def is_number(e: str) -> bool:
	"""Returns is it a number or no... isnumeric() returns False when '-1'
	:param e: str
	:return: True or False
	"""
	try:
		int(e)
		return True
	except ValueError:
		return False


def is_web3(connection):
	"""
	Checks and return the connection if it's Web3. Otherwise, throws an error
	"""
	if not isinstance(connection, Web3):
		raise TypeError("Can't create Manager because got wrong Connection type. "
						f"Should be {Web3} object, got: {connection}")
	return connection


def check_save_load_files():
	"""Checks if the directory and files exist.
	If everything exist - does nothing.
	If nothing exist - creates everything.
	For more - read the code ^_^					"""
	def create_cryptography_key():				# Meth to create cryptography key
		with open(settings.crypto_key, "wb") as w:
			w.write(Fernet.generate_key())

	if not os.path.isdir(settings.folder):			# If no Folder, then create:
		os.mkdir(settings.folder)					# - folder
		open(settings.saved_wallets, "w").close()	# - file
		create_cryptography_key()					# - cryptography key
	else:
		# if File and Key exists - do Nothing.
		if os.path.exists(settings.saved_wallets) and os.path.exists(settings.crypto_key):
			return 	# The most popular situation, put upfront to save time on useless checks...

		# no File - no Key		-->> create files
		if not os.path.exists(settings.saved_wallets) and not os.path.exists(settings.crypto_key):
			open(settings.saved_wallets, "w").close()  	# create file
			create_cryptography_key()  					# create cryptography key

		# no File - yes Key		-->> create file
		elif not os.path.exists(settings.saved_wallets) and os.path.exists(settings.crypto_key):
			open(settings.saved_wallets, "w").close()  	# create file

		# yes File - no Key		-->> problem.. rename old_file and create new key + file
		else:
			# creation_date_in_ns = os.stat(settings.saved_wallets).st_birthtime	# get the date of creation in ns
			# creation_date = str(date.fromtimestamp(creation_date_in_ns))			# transform into YYYY-MM-DD
			creation_date = str(date.fromtimestamp(os.stat(settings.saved_wallets).st_birthtime))	# one line
			os.rename(settings.saved_wallets,  f"{settings.saved_wallets}_old_{creation_date}")

			print(":::: rename - create K F")
			open(settings.saved_wallets, "w").close()  	# create file
			create_cryptography_key()  					# create cryptography key


def get_fernet_key():
	with open(settings.crypto_key, "rb") as r:
		return r.read()


def print_wallets(list_with_wallets):
	length = len(list_with_wallets)
	for i in range(length):  									# print all addresses
		print(f"{i + 1}. {list_with_wallets[i].get_info()}")  	# with its index


def print_all_info(list_with_wallets):
	length = len(list_with_wallets)
	for i in range(length):											# prints info with TXs
		print(f"{i + 1}. {list_with_wallets[i].get_all_info()}")  	# and its index


def print_all_txs(web3: Web3):
	chainId = web3.eth.chain_id
	for tx in services.manager.Manager.all_txs:		# prints all TXs
		if chainId == tx.chainId:					# with current network
			print(tx)


def generate_label(set_with_labels):
	while True:
		number = int(random() * 10**5)			# generate number
		if number >= 10000:						# if it's >= 10000
			label = str(number)
			if label not in set_with_labels:	# check it's unique
				return label					# return


def ask_label(set_with_labels):
	while True:
		label = input(text.add_ask_label).strip()
		if not label:								# If empty - generate 5 digits number
			return generate_label(set_with_labels)

		if label.lower() == "exit":  				# If not empty - check if "exit"
			raise Exception("Exited while tried to write the label")

		if label in set_with_labels:  			# Then check if the label exist
			print("This label is exist. Try another")
		else:  										# if not - return it
			return label


def update_wallet(web3, wallet):
	"""
	Receives Wallet. If the wallet doesn't have an address - method parses it and adds
	After that it updates balance and transaction count
	"""
	if isinstance(wallet, Wallet):
		if not wallet.addr:  						# if the wallet doesn't have address
			key = wallet.key()  										# get private key
			wallet.addr = Account.privateKeyToAccount(key).address  	# parse the address and add

		wallet.balance_in_wei = web3.eth.get_balance(wallet.addr)  		# update balance
		wallet.nonce = web3.eth.get_transaction_count(wallet.addr)  	# update nonce

		# update Tx if needed (status is None)
		[trans.update_tx(web3, tx) for tx in wallet.txs if tx.status is None]
	else:
		print(text.upd_error_not_wallet)


def generate_wallet(web3, set_labels, set_keys, result_list):
	"""Generates unique 1 wallet (key + label). Updates it and add to the list
	"""
	key = web3.toHex(web3.eth.account.create().key)  	# get private key
	if key not in set_keys:  					# check we don't have it
		label = generate_label(set_labels)  	# generate unique label
		wallet = Wallet(key, label)  			# create wallet
		update_wallet(web3, wallet)				# update it

		result_list.append(wallet)				# save it

		print(".", end="")  # just "progress bar"
	else:										# If we have that key - try again... tho I doubt it
		generate_wallet(web3, set_labels, set_keys, result_list)	# just in case...


def generate_wallets(web3, set_labels, set_keys, number) -> list:
	"""Generates wallets and returns list with updates wallets
	:return: list with updated Wallets
	"""
	new_generated_wallets = list()
	list_daemons = list()
	print(f"Started the generation {number} wallets. Progress bar: ", end="")

	for _ in range(number):					# Do N times
		if threads.can_create_daemon():		# If we can create daemon - do it
			daemon = threads.start_todo(generate_wallet, False,					# create daemon
						web3, set_labels, set_keys, new_generated_wallets)		# to do generate_wallet()
			list_daemons.append(daemon)											# add to the list
		else:								# If we can't create - sleep and wait
			time.sleep(settings.wait_to_create_daemon_again)

	[daemon.join() for daemon in list_daemons if daemon.is_alive()]				# wait till they finish
	print(" Finished")															# print &
	return new_generated_wallets												# return the list


def get_wallet_index_by_text(wallets_list: list, set_addr: set, string) -> int:
	"""
	:param wallets_list: list with wallets
	:param set_addr: set with addresses
	:param string: address or number of the wallet
	:return: Index of selected Wallet in the list
	"""
	total_wallets = len(wallets_list)

	if is_number(string):  # get number if it's number
		number = int(string)
		if number > total_wallets or number < 1:		# if N > wallets in list or < 1
			raise IndexError("Wrong number")  			# throw IndexError
		return number - 1  								# if not - return Index
	elif not string.startswith("0x") or len(string) != settings.address_length:
		raise Exception(text.error_not_number_or_address)
	else:
		if string not in set_addr:  # if there's no such wallet
			raise Exception(text.error_no_such_address)  # throw error
		else:
			for index in range(total_wallets):  # else find its Index
				if wallets_list[index].addr == string:
					return index  # end return


def delete_txs_history():
	if not services.manager.Manager.all_txs:
		print(text.text_no_tx)
	else:
		for tx in services.manager.Manager.all_txs:  # and them delete everything.
			tx.delete()
			del tx

		services.manager.Manager.all_txs.clear()
		print(text.success)


def init_all_txs(wallets_list):
	unique_txs = services.manager.Manager.all_txs

	for wallet in wallets_list: 	# for ear wallet
		if not wallet.txs:  		# check do they have txs
			continue  				# if no - next wallet
		else:
			for tx in wallet.txs:  			# if yes - for each tx in txs
				if tx not in unique_txs:  	# if we don't have in our unique list
					unique_txs.add(tx)  	# add