import pickle
import time
from eth_account import Account

from config import settings, texts
from random import random
from web3 import Web3
from datetime import date
from cryptography.fernet import Fernet
from services.classes import Wallet
from services import threads, trans, manager
import os


"""
File with general methods to alleviate Manager (make it easy to read)
Not important methods/functions which doesn't work with data directly will be here
"""


def confirm():
	return input("Are you sure? Write \"y\" to confirm: ").lower() == "y"


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
	"""Checks and return the connection if it's Web3. Otherwise, throws an error"""
	if not isinstance(connection, Web3):
		raise TypeError("Can't create Manager because got wrong Connection type. "
						f"Should be {Web3} object, got: {connection}")
	return connection


def get_fernet_key():
	with open(settings.crypto_key, "rb") as r:
		return r.read()


def print_wallets(list_with_wallets):
	"""Prints wallets with its index"""
	length = len(list_with_wallets)
	for i in range(length):  						# print all addresses
		print(f"{i + 1}. {list_with_wallets[i]}")  	# with its index


def print_all_info(list_with_wallets):
	"""Prints wallets with its index and TXs list"""
	length = len(list_with_wallets)
	for i in range(length):											# prints info with TXs
		print(f"{i + 1}. {list_with_wallets[i].get_all_info()}")  	# and its index


def print_all_txs(web3: Web3):
	"""Prints all TXs with current network (chainId)"""
	chainId = web3.eth.chain_id
	for tx in manager.Manager.all_txs:		# prints all TXs
		if chainId == tx.chainId:					# with current network
			print(tx)


def print_txs_for_wallet(chainId: int, wallet: Wallet):
	"""Prints wallet all txs for the wallet in given network"""
	print(settings.chain_name[chainId] + " | " + wallet.__str__())
	update_txs_for_wallet(wallet)

	for tx in wallet.txs:
		if tx.chainId == chainId:
			print("\t" + tx.str_no_bc())


def generate_label(set_with_labels):
	while True:
		number = int(random() * 10**5)			# generate number
		if number >= 10000:						# if it's >= 10000
			label = str(number)
			if label not in set_with_labels:	# check it's unique
				return label					# return


def ask_label(set_with_labels):
	while True:
		label = input(texts.add_ask_label).strip()
		if not label:								# If empty - generate 5 digits number
			return generate_label(set_with_labels)

		if label.lower() == "exit":  				# If not empty - check if "exit"
			raise Exception("Exited while tried to write the label")

		if label in set_with_labels:  			# Then check if the label exist
			print("This label is exist. Try another")
		else:  										# if not - return it
			return label


def update_wallet(web3: Web3, wallet: Wallet, set_labels: set):
	"""
	Receives Wallet. If the wallet doesn't have an address - method parses it and adds
	After that it updates balance and transaction count
	"""
	if isinstance(wallet, Wallet):
		if not wallet.addr or not wallet.addr_lower:  					# if the wallet doesn't have address
			key = wallet.key()  										# get private key
			wallet.addr = Account.privateKeyToAccount(key).address  	# parse the address and add
			wallet.addr_lower = wallet.addr.lower()

		if wallet.label is None:
			wallet.label = generate_label(set_labels)

		wallet.balance_in_wei = web3.eth.get_balance(wallet.addr)  		# update balance
		wallet.nonce = web3.eth.get_transaction_count(wallet.addr)  	# update nonce

		update_txs_for_wallet(wallet)		# updates txs list and each tx if status == None
		[trans.update_tx(web3, tx) for tx in wallet.txs if tx.status is None]
	else:
		print(texts.upd_error_not_wallet)


def generate_wallet(web3, set_labels, set_keys, result_list):
	"""Generates unique 1 wallet (key + label). Updates it and add to the list
	"""
	key = web3.toHex(web3.eth.account.create().key)  	# get private key
	if key not in set_keys:  					# check we don't have it
		label = generate_label(set_labels)  	# generate unique label
		wallet = Wallet(key, label)  			# create wallet
		update_wallet(web3, wallet, set_labels)		# update it

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


def get_wallet_index_by_str(wallets_list: list, set_addr: set, addr: str) -> int:
	"""
	:param wallets_list: list with wallets
	:param set_addr: set with addresses
	:param addr: number (starts from 1)
	:return: Index of selected Wallet in the list
	"""
	total_wallets = len(wallets_list)

	if is_number(addr):  # get number if it's number
		number = int(addr)
		if number > total_wallets or number < 1:		# if N > wallets in list or < 1
			raise IndexError("Wrong number")  			# throw IndexError
		return number - 1  								# if not - return Index
	elif not addr.startswith("0x") or len(addr) != settings.address_length:
		raise Exception(texts.error_not_number_or_address)
	else:
		if addr not in set_addr:  							# if there's no such wallet
			raise Exception(texts.error_no_such_address)  	# throw error
		else:
			addr = addr.lower()
			for i in range(total_wallets):  		# else find its Index
				if wallets_list[i].addr_lower == addr:
					return i  						# end return


def delete_txs_history(wallets: list):
	if manager.Manager.all_txs:
		[wallet.txs.clear() for wallet in wallets]		# delete TXs from wallets
		manager.Manager.all_txs.clear()					# clear the set


def update_txs_for_wallet(wallet):
	for tx in manager.Manager.all_txs:
		if (wallet.addr == tx.receiver or wallet.addr == tx.sender) and tx not in wallet.txs:
			wallet.txs.append(tx)


def check_saveloads_files(folder: str, path_to_file: str):
	"""Checks if the directory and files exist.
	If everything exist - does nothing.
	If nothing exist - creates everything.
	For more - read the code ^_^
	:param folder: 			str -> "folder/"
	:param path_to_file: 	str -> "folder/name_of_your_file"
	"""
	def create_cryptography_key():  # Meth to create cryptography key
		key = Fernet.generate_key()
		with open(settings.crypto_key, "wb") as w:
			w.write(key)
		print(key)
		return key

	if not os.path.isdir(folder):  	# If no Folder, then create:
		os.mkdir(folder)  							# - folder
		open(path_to_file, "w").close()  			# - file
		return create_cryptography_key()  			# - cryptography key

	# if File and Key exists - do Nothing		<<-- the most frequent situation
	if os.path.exists(path_to_file) and os.path.exists(settings.crypto_key):
		return get_fernet_key()

	# no File - no Key		-->> create files
	if not os.path.exists(path_to_file) and not os.path.exists(settings.crypto_key):
		open(path_to_file, "w").close()  			# create file
		return create_cryptography_key()  			# create cryptography key

	# no File - yes Key		-->> create file
	if not os.path.exists(path_to_file) and os.path.exists(settings.crypto_key):
		open(path_to_file, "w").close()  			# create file
		return get_fernet_key()  					# create cryptography key

	# yes File - no Key		-->> problem.. rename old_file and create new key + file

	# creation_date_in_ns = os.stat(settings.saved_wallets).st_birthtime			# get the date of creation in ns
	# creation_date = str(date.fromtimestamp(creation_date_in_ns))					# transform into YYYY-MM-DD
	# above in one line
	creation_date = str(date.fromtimestamp(os.stat(path_to_file).st_birthtime))
	os.rename(path_to_file, f"{path_to_file}_old_{creation_date}")  				# rename
	open(settings.saved_wallets, "w").close()  		# create file
	return create_cryptography_key()  				# create cryptography key


def save_data(data, folder, filepath):
	"""
	Received folder name and file name. Saves encoded data to folder/name_file
	:param data: 		data to save (if empty - will clear the file)
	:param folder: 		str -> "folder/"
	:param filepath: 	str -> "folder/name_of_your_file"
	:return: loaded obj or None
	"""
	if not data:						# if empty
		open(filepath, "w").close()		# clear the file
	else:
		key = check_saveloads_files(folder, filepath)		# check data and get secret
		fernet = Fernet(key)								# get key from secret

		data_to_save = fernet.encrypt(pickle.dumps(data))	# dumps -> encode
		with open(filepath, "wb") as w:						# write
			w.write(data_to_save)


def load_data(folder, filepath):
	key = check_saveloads_files(folder, filepath)		# check data and get secret
	fernet = Fernet(key)								# get key from secret

	with open(filepath, "rb") as r:
		encrypted_bytes = r.read()

	if encrypted_bytes:
		bytes_ = fernet.decrypt(encrypted_bytes)
		return pickle.loads(bytes_)
	else:
		return None