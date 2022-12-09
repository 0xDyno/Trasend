# Import my files
from config import text, settings
from wallet import Wallet
import assist

# Import third-party files
from web3 import Web3
from threading import *
from time import sleep
from cryptography.fernet import Fernet
import pickle


class Manager:
	"""
	Class Manager to manage wallets and all operations that change data directly
	All operations that don't change data directly located in assist.py
	All operations that related to transaction located in trans.py
	"""

###################################################################################################
# Params ##########################################################################################
###################################################################################################

	__singleton = None
	web3: Web3 = None
	wallets_list = list()

	# added from wallets_list when __init__
	set_keys = set()
	set_labels = set()
	set_addr = set()

	# other params
	last_block = None			# updates every N secs by daemon
	is_main_finished = False	# flag for daemons

###################################################################################################
# Initialization / Save-Load ######################################################################
###################################################################################################

	def new_connection(self, connection):
		assist.is_web3(connection)
		self.web3 = connection

	def __new__(cls, *args, **kwargs):
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)

		return cls.__singleton

	def __del__(self):
		self.is_main_finished = True
		Manager.__singleton = None

	def __init__(self, connection):
		"""
		 If object creates first time - it will ask for Web3 object
		 If second time - it will use connection from 1st time
		 To change connection - use obj.new_connection(new_Web3)
		"""
		if self.web3 is None:
			assist.is_web3(connection)
			self.web3 = connection

			# Get status of the connection
			print(f"Connection status: {self.web3.isConnected()}")

			# Loading addresses
			self.__singleton.load_list_with_wallets()

			# Init sets if there are wallets
			if not self.__singleton.wallets_list:
				print(text.new_text_no_wallets_to_init)
			else:
				self.__singleton.update_wallets()
				self.__singleton.initialize_sets()

			# Start a demon to regularly update info (last block)
			self.daemon_to_update_last_block = None
			self.start_daemon_to_update_last_block()
		else:
			print(f"Connection status: {self.web3.isConnected()}")

	def update_wallets(self):
		if self.wallets_list:
			print(text.upd_text_updating_wallets, end=" ")
			for wallet in self.wallets_list:
				assist.update_wallet(self.web3, wallet)
			print(text.success)
		else:
			print(text.upd_text_no_wallets_to_update)

	def initialize_sets(self):
		print(text.sets_text_init_sets, end=" ")
		for wallet in self.wallets_list:
			self.add_to_sets(wallet)
		print(text.success)

	def start_daemon_to_update_last_block(self):
		# Update the last block forever every N seconds
		def work_for_daemon():
			while not self.is_main_finished:
				self.update_last_block()
				if settings.print_daemons_info:
					print("Daemon, updated the last block, current block is", self.last_block["number"])
				sleep(settings.ETH_block_time)

		# create a Daemon to do work in work_for_daemon()
		self.daemon_to_update_last_block = Thread(target=work_for_daemon)
		self.daemon_to_update_last_block.start()

###################################################################################################
# Save-Load #######################################################################################
###################################################################################################

	def save_wallets_list(self):
		assist.check_save_load_files()
		fernet = Fernet(assist.get_fernet_key())

		if not self.wallets_list:  							# If no wallets in the list - clear file
			open(settings.saved_wallets, "w").close()
		else:
			data_to_save = bytes()
			# For each wallet in the list - dump it and add separator
			for wallet in self.wallets_list:
				data_to_save = data_to_save + pickle.dumps(wallet) + settings.separator.encode()

			with open(settings.saved_wallets, "wb") as w:  	# Save data with wallets
				w.write(fernet.encrypt(data_to_save))		# after fernet encrypt it

	def load_list_with_wallets(self):
		print(text.new_text_load_the_wallets, end=" ")		# Beginning - tell started to work
		assist.check_save_load_files()
		fernet = Fernet(assist.get_fernet_key())

		with open(settings.saved_wallets, "rb") as r:		# get Bytes
			bytes_ = r.read()

		if not bytes_:
			print(text.new_text_not_wallets_to_load)		# End - tell no wallets to load
		else:
			decrypted_bytes = fernet.decrypt(bytes_)  		# decrypt Bytes

			for element in decrypted_bytes.split(settings.separator.encode()):
				if element: 								# if element - exist
					wallet = pickle.loads(element)			# load
					self.wallets_list.append(wallet)		# add
			print(text.success)								# End - tell success

###################################################################################################
# Default methods #################################################################################
###################################################################################################

	def add_wallet(self, wallet: Wallet):
		"""Adds wallet into the list and sets"""
		if not isinstance(wallet, Wallet):
			raise TypeError("I can add only wallet and that's not wallet. Tell the devs")
		else:
			if not wallet.addr:								# if no addr
				assist.update_wallet(self.web3, wallet)		# get it

			self.wallets_list.append(wallet)				# add to the list
			self.add_to_sets(wallet)						# add to the sets

	def delete_wallet(self, wal=0):
		"""
		Deletes wallet from list and sets by its Index in the list or Wallet obj.
		If no argument - deletes the last one
		:param wal: Wallet obj or number
		"""
		if isinstance(wal, Wallet):						# if it's wallet - get it's index
			for i in range(len(self.wallets_list)):
				if wal is self.wallets_list[i]:
					wal = i

		if isinstance(wal, int):
			wallet = self.wallets_list.pop(wal)  				# del from the list
			self.delete_from_sets(wallet)  						# del from the sets
			print(text.del_successfully_deleted, wallet.addr)  	# print about success
			del wallet
		else:
			raise TypeError("It's not wallet or index, I don't work with it. Tell the devs")

	def try_add_wallet(self):
		"""Checking one by one has the same speed as using a batch.
		Now I implement import one by one. Later I can add import batch of private keys.
		"""
		while True:
			try:
				print(text.add_input_private_key)
				key = input().strip().lower()
				if not key or key == "exit":
					break
				# If starts not with 0x or length not 66 symbols - tell about mistake
				if not key.startswith("0x") or len(key) != settings.private_key_length:
					print(text.add_error_wrong_format)
					continue
				elif key in self.set_keys:  		# If exits - tell the label of the wallet
					label = "Unknown.. tell the devs"
					for wallet in self.wallets_list:  		# find this wallet
						if key == wallet.key():  			# if this wallet - same what the user wrote
							label = wallet.label  			# get the label
							break  							# stop and write it
					print(f"Error, the key is already added to the system with the label: \"{label}\"")
				else:  	# If OK - add the wallet
					label = assist.ask_label(self.set_labels)  	# ask label
					wallet = Wallet(key, label)  				# create Wallet
					assist.update_wallet(self.web3, wallet)  	# update info

					self.add_wallet(wallet)					# add wallet
					print(f"Successfully added the wallet: {wallet.get_all_info()}")
			except Exception as e:
				# raise Exception(e)
				print(f"Something wrong, mistake: {e}\nTry again.")

	def try_delete_wallet(self):
		""" Realisation of deleting wallets -> certain wallet, last, last N or all """
		while True:
			try:
				if not self.wallets_list:						# If no wallets
					print(text.del_no_wallets)					# tell about it
					return										# and return

				print(text.del_instruction_to_delete_wallet)	# instruction
				assist.print_wallets(self.wallets_list)  		# print wallets
				print("---------------------")					# and line

				line = input().strip()							# parse the input
				if not line or line.lower() == "exit":
					return

				# Processing the input
				process_line = line.lower()
				if process_line.startswith("last"):

					if process_line == "last":							# if only last
						how_many_delete = 1								# it's 1 wallet
					else:
						how_many_delete = int(line.split(" ")[1])		# otherwise parse how many

					for i in range(how_many_delete):					# do N times
						last_index = len(self.wallets_list) - 1			# - get last index
						self.delete_wallet(last_index)			# - delete it
				elif process_line == "all":
					for i in range(len(self.wallets_list)):		# delete all
						self.delete_wallet()
				else:											# else get wallet index
					index = assist.get_wallet_index_by_text(self.wallets_list.copy(),
															self.set_addr.copy(),
															process_line)
					self.delete_wallet(index)					# delete it
			except Exception as e:
				print("Something went wrong:", e, end="\n\n")

	def generate_wallets(self, number=1):
		if number > 100:
			print(text.error_more_than_100)
		else:
			# get the list with new generated wallets
			new_generated_wallets = assist.generate_wallets(self.web3,
															self.set_labels.copy(),
															self.set_keys.copy(),
															number)
			# add it to our list
			for wallet in new_generated_wallets:
				self.add_wallet(wallet)

			# print generated wallets info
			print("Generated wallets:")
			for wallet in new_generated_wallets:
				print(wallet.addr, wallet.key())

	def add_to_sets(self, wallet):
		"""Adds new wallet to sets if there's no such wallet.
		If there's same data - throws Exception"""
		# if any field in the set - throw error. Else - add new wallet
		if wallet.key() in self.set_keys or \
			wallet.label in self.set_labels or \
			wallet.addr in self.set_addr:

			raise Exception(text.error_add_to_set)
		else:
			self.set_keys.add(wallet.key())
			self.set_labels.add(wallet.label)
			self.set_addr.add(wallet.addr)

	def delete_from_sets(self, wallet):
		""" Deletes wallet from the sets if every field is in sets. Otherwise, throws Exception """
		if wallet.key() in self.set_keys and \
			wallet.label in self.set_labels and \
			wallet.addr in self.set_addr:

			self.set_keys.remove(wallet.key())
			self.set_labels.remove(wallet.label)
			self.set_addr.remove(wallet.addr)
		else:
			raise Exception(text.error_delete_from_set)

	def print_block_info(self, block_number=None):
		"""
		Prints info about transferred block
		or the last block if block_number is None
		:param block_number: str or int of the block
		:return: nothing
		"""
		# We have to know info about the last block
		if not self.check_last_block():
			print(text.error_no_info_about_last_block)
			return

		# We need to know that's the argument is not None. If None - use Last Block
		if block_number is None:
			block = self.last_block
		else:
			# So we have argument, need to check it and get that block
			if block_number.isnumeric():
				block_number = int(block_number)

			# Check the asked block is smaller than the last one
			if block_number > self.last_block["number"]:
				print(text.error_block_doesnt_exist_yet)
				return
			else:
				block = self.web3.eth.get_block(block_number)

		for k, v in block.items():					# get key and value
			print(k, end=" >>> ")						# print key, no \n

			if isinstance(v, bytes):								# if Value is bytes
				print(self.web3.toHex(v))		# decode Value and print
			elif isinstance(v, list):			# if Value is list
				if not v:						# list empty - print \n
					print()
				else:							# not empty
					for el in v:				# decode and print all elements
						print(self.web3.toHex(el))
			else:								# if Value not list and not bytes - print it
				print(v)

	def check_last_block(self) -> bool:
		"""
		Checks that the last block is exist.
		If it doesn't exist - tries to update it

		:return: True or False
		"""
		if self.last_block is not None:
			return True
		else:
			print("No info about the last block, updating...", sep=" ")
			self.update_last_block()

			if self.last_block is not None:
				print(text.success)
				return True
			else:
				print(text.fail)
				return False

###################################################################################################
# Assist methods ##################################################################################
###################################################################################################

	def update_last_block(self):
		self.last_block = self.web3.eth.get_block("latest")

	def print_wallets(self):
		assist.print_wallets(self.wallets_list.copy())

###################################################################################################
# Finish ##########################################################################################
###################################################################################################

	def finish_work(self):
		self.save_wallets_list()

		# Finish the demon
		self.is_main_finished = True