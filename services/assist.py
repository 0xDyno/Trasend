import os
import pickle
import time
from web3 import Web3
from eth_account import Account

from cryptography.fernet import Fernet
from random import random
from datetime import date, datetime

from config import settings, texts
from services.classes import Wallet, Token
from services import threads, trans, manager, logs

"""
File with general methods to alleviate Manager (make it easy to read)
Not important methods/functions which doesn't work with data directly will be here
"""


def confirm(print_before=None):
	if print_before is not None:
		print(print_before)
	return input("> Are you sure? Write \"y\" to confirm: ").lower().strip() == "y"


def is_it_addr(line: str) -> bool:
	"""return True if it's like address. False - if it's 100% not address"""
	return line.startswith("0x") and len(line) == settings.address_length


def is_it_key(line: str) -> bool:
	"""return True if it's like private key. False - if it's 100% not private key"""
	return line.startswith("0x") and len(line) == settings.private_key_length


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


def print_all_txs(chain_id: int):
	"""Prints all TXs with current network (chainId)"""
	for tx in manager.Manager.all_txs:		# prints all TXs
		if chain_id == tx.chain_id:					# with current network
			print(tx)


def print_txs_for_wallet(chain_id: int, wallet: Wallet):
	"""Prints wallet all txs for the wallet in given network"""
	print(settings.chain_name[chain_id] + " | " + wallet.__str__())
	update_txs_for_wallet(wallet)

	for tx in wallet.txs:
		if tx.chain_id == chain_id:
			print("\t" + tx.str_no_bc())


def generate_label(set_with_labels):
	"""Generates unique label from numbers in defined length from settings"""
	while True:
		number = int(random() * 10 ** settings.label_gen_length)	# it works..
		if number >= 10 ** (settings.label_gen_length - 1):
			label = str(number)
			if label not in set_with_labels:	# check it's unique
				return label					# return


def ask_label(set_with_labels: set):
	min_ = settings.label_min_length
	max_ = settings.label_max_length
	print(texts.ask_label_instruction)
	while True:
		label = input("\t>> ").strip()
		if not label:									# If empty - generate number
			return generate_label(set_with_labels)
		elif label.lower() == "exit":  					# If "exit" - exit
			raise InterruptedError(texts.exited)
		elif len(label) > max_ or len(label) < min_:	# If length < min or > than max
			print(texts.label_wrong_length.format(min_, max_, len(label)))
			continue

		if not label.isalnum():
			print(texts.label_wrong_letters)
			continue

		if label in set_with_labels:  			# Then check if the label exist
			print(texts.label_exist)
		else:  										# if not - return it
			return label


def update_wallet(w3: Web3, wallet: Wallet, set_labels: set, update_tx=False):
	"""
	Receives Wallet. If the wallet doesn't have an address - method parses it and adds
	After that it updates balance and transaction count
	"""
	assert isinstance(wallet, Wallet), texts.error_cant_update
	if not wallet.addr or not wallet.addr_lower:  					# if the wallet doesn't have address
		key = wallet.key()  										# get private key
		wallet.addr = Account.privateKeyToAccount(key).address  	# parse the address and add
		wallet.addr_lower = wallet.addr.lower()

	if wallet.label is None:
		wallet.label = generate_label(set_labels)

	wallet.balance_in_wei = w3.eth.get_balance(wallet.addr)  		# update balance
	wallet.nonce = w3.eth.get_transaction_count(wallet.addr)  		# update nonce

	if update_tx:
		update_txs_for_wallet(wallet)  # updates txs list and each tx if status == None
		[trans.update_tx(w3, tx) for tx in wallet.txs if tx.status is None]


def generate_wallet(w3, set_labels, set_keys, result_list):
	"""Generates unique 1 wallet (key + label). Updates it and add to the list
	"""
	key = w3.toHex(w3.eth.account.create().key) 	# get private key
	if key not in set_keys:  						# check we don't have it
		label = generate_label(set_labels)  		# generate unique label
		wallet = Wallet(key, label)  				# create wallet
		update_wallet(w3, wallet, set_labels)		# update it

		result_list.append(wallet)				# save it
	else:										# If we have that key - try again... tho I doubt it
		generate_wallet(w3, set_labels, set_keys, result_list)	# just in case...


def generate_wallets(w3, set_labels, set_keys, number) -> list:
	"""Generates wallets and returns list with updates wallets
	:return: list with updated Wallets
	"""
	new_generated_wallets = list()
	list_daemons = list()
	print(f"> Started the generation {number} wallets")
	for _ in range(number):
		while not threads.can_create_daemon():		# If we can create daemon - sleep
			if number > 50:
				create_progress_bar(len(new_generated_wallets), number)
			time.sleep(settings.wait_to_create_daemon_again)

		daemon = threads.start_todo(generate_wallet, False, w3, set_labels, set_keys, new_generated_wallets)
		list_daemons.append(daemon)										# add to the list
	[daemon.join() for daemon in list_daemons if daemon.is_alive()]		# wait till they finish
	return new_generated_wallets										# return the list


def get_wallet_index(wallets_list: list, set_addr: set, set_labels: set, line: str | Wallet) -> int:
	"""
	Returns wallet index in the list from: Waller obj or it's number, label or address.
	:param wallets_list: list with wallets
	:param set_addr: set with addresses
	:param set_labels: set with labels
	:param line: address or label or number (starts from 1)
	:return: Index of selected Wallet in the list
	"""
	if isinstance(line, Wallet):
		for i in range(len(wallets_list)):
			if wallets_list[i].key() == line.key():
				return i

	if line.isnumeric() and len(line) < 4:		# Min length for label = 4 chars.
		number = int(line)						# If it's less -> that's number
		assert len(wallets_list) >= number > 0, "Wrong number"
		return number - 1
	# Tho... that should be addr or label, let's check it
	assert line in set_addr or line in set_labels, texts.error_no_such_address

	line = line.lower()
	for i in range(len(wallets_list)):
		if wallets_list[i].addr_lower == line or wallets_list[i].label == line:
			return i


def get_addrs_from_input():
	addr_list = list()
	while True:
		read_line = input()
		if read_line.lower() == "done":
			return addr_list
		try:
			addr = Web3.toChecksumAddress(read_line)
			addr_list.append(addr)
		except ValueError:
			print("Wrong address, check for mistake -", read_line)


def delete_txs_history(wallets: list):
	if manager.Manager.all_txs:
		[wallet.txs.clear() for wallet in wallets]		# delete TXs from wallets
		manager.Manager.all_txs.clear()					# clear the set


def update_txs_for_wallet(wallet):
	if wallet.txs:							# skip 1 check on each iteration if there are no txs at all
		for tx in manager.Manager.all_txs:
			if (wallet.addr == tx.receiver or wallet.addr == tx.sender) and tx not in wallet.txs:
				wallet.txs.append(tx)
	else:
		for tx in manager.Manager.all_txs:
			if wallet.addr == tx.receiver or wallet.addr == tx.sender:
				wallet.txs.append(tx)


def is_contract_exist(chain_id, sc_addr) -> bool:
	"""Checks that we have smart contract info in correct chain"""
	tokens_set = manager.Manager.dict_sc_addr.get(chain_id)
	if not tokens_set:  			# get set with correct chain id
		return False				# if empty = no tokens
	if sc_addr not in tokens_set:  	# if not in set - False
		return False
	return True


def get_smart_contract_if_have(chain_id, sc_addr) -> Token | bool:
	"""Check if the tokens exists in the system and returns it, otherwise returns False"""
	if is_contract_exist(chain_id, sc_addr):
		for token in manager.Manager.all_tokens:
			if token.chain_id == chain_id and token.sc_addr == sc_addr:
				return token
	return False


def add_smart_contract_token(chain_id: int, sc_addr: str, symbol: str, decimal: int, abi="default"):
	if not is_contract_exist(chain_id, sc_addr):					# if new one
		new_token = Token(chain_id, sc_addr, symbol, decimal, abi)		# create Token
		print(chain_id)
		print(sc_addr)
		print(symbol)
		print(decimal)
		print(type(manager.Manager.dict_sc_addr), manager.Manager.dict_sc_addr)
		print(type(manager.Manager.dict_sc_addr.get(chain_id)), manager.Manager.dict_sc_addr.get(chain_id))
		manager.Manager.dict_sc_addr.get(chain_id).add(sc_addr)			# add addr to addr_set in correct chain if
		manager.Manager.all_tokens.add(new_token)						# and add Obj to global set


def export_wallets(wallets: list):
	time_ = str(datetime.strftime(datetime.fromtimestamp(time.time()), "%Y_%H%M%S"))
	path = os.path.join(os.getcwd() + "/" + settings.folder + "wallet_export_" + time_ + ".txt")
	with open(path, "w") as w:
		for wallet in wallets:
			w.write(f"{wallet.addr} {wallet.key()}\n")
	print("> Wallets were exported to >", path)


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


# Some Not Important Methods...


def create_progress_bar(current, finish):
	"""Just "progress bar" """
	step = 1.005
	while finish > 80:				# equalize to 100 max
		finish = finish / step
		current = current / step
	while finish < 80:
		finish = finish * step
		current = current * step
	current = int(current)
	finish = 80 - current

	print("." * current, end="")
	print(" " * finish, end="")
	current = int(current * 1.26)
	if current < 10:
		print(f" | ( {current}% / 100%)")
	else:
		print(f" | ({current}% / 100%)")
