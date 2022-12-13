# Import my files
from config import texts, settings
from services.classes import Wallet
from services import assist, trans, threads, logs

# Import third-party files
from web3 import Web3
import time


def save_txs():
	assist.save_data(Manager.all_txs, settings.folder, settings.saved_txs)


def load_txs():
	print(texts.loading_txs, end=" ")  	# Start
	loaded_data = assist.load_data(settings.folder, settings.saved_txs)
	if loaded_data is None:
		print(texts.no_txs_to_load)  	# End - Tell no wallets to load
	else:
		Manager.all_txs = loaded_data
		print(texts.success)  					# End - Success


class Manager:
	"""
	Class Manager to manage wallets and all operations that change data directly
	All operations that don't change data directly located in assist.py
	All operations that related to transaction located in trans.py
	"""
	__singleton = None
	all_txs = list()
	network_gas_price = None
	network_max_priority = None
	gas_price = None
	max_priority = None

###################################################################################################
# Initialization ##################################################################################
###################################################################################################

	def __new__(cls, *args, **kwargs):
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)
			cls.__singleton.is_initialized = False

		return cls.__singleton

	def __del__(self):
		Manager.__singleton = None

	def __init__(self, connection):
		"""
		 If object creates first time - it will init everything
		 If second time - it will use data from 1st time
		"""
		if not self.is_initialized:
			assert isinstance(connection, Web3), texts.error_not_web3.format(connection, Web3)
			self.is_initialized = True
			self.w3 = connection

			# Main params:
			self.chain_id = self.w3.eth.chain_id

			self.wallets = list()
			self.set_keys = set()
			self.set_labels = set()
			self.set_addr = set()
			self.last_block = None  	# updates every N secs by daemon

			self._load_wallets()		# Load addresses
			load_txs()					# Load Txs

			# Init sets if there are wallets
			if self.wallets:
				print(texts.init_files, end=" ")
				self.update_wallets()
				self._initialize_sets()
				self._initialize_txs()
			print(texts.init_finished)

			# Start a demon to regularly update info (last block)
			threads.start_todo(self._daemon_update_last_block, True)
			threads.start_todo(self._daemon_update_gas, True)
		else:
			print(f"Connection status: {self.w3.isConnected()}")

	def new_connection(self, connection: Web3):
		assert isinstance(connection, Web3), texts.error_not_web3.format(connection, Web3)
		self.w3 = connection
		self.chain_id = self.w3.eth.chain_id

###################################################################################################
# Inner methods ###################################################################################
###################################################################################################

	def _initialize_sets(self):
		"""Init sets with wallet info"""
		for wallet in self.wallets:  		# for each wallet
			self._add_to_sets(wallet)  		# add to sets

	def _initialize_txs(self):
		"""From all_tx init wallets with related tx
		(if this wallet related to tx - adds tx into wallet's list)"""
		for wallet in self.wallets:
			assist.update_txs_for_wallet(wallet)

	def _add_to_sets(self, wallet):
		"""Adds new wallet to sets if there's no such wallet.
		If there's same data - throws Exception"""
		# if any field in the set - throw error. Else - add new wallet
		if wallet.key() in self.set_keys \
			or wallet.label in self.set_labels \
			or wallet.addr_lower in self.set_addr:

			raise ValueError(texts.error_add_to_set)
		self.set_keys.add(wallet.key())
		self.set_labels.add(wallet.label)
		self.set_addr.add(wallet.addr_lower)

	def _delete_from_sets(self, wallet):
		""" Deletes wallet from the sets if every field is in sets. Otherwise, throws Exception """
		if wallet.key() not in self.set_keys \
			or wallet.label not in self.set_labels \
			or wallet.addr_lower not in self.set_addr:

			raise ValueError(texts.error_delete_from_set)
		self.set_keys.remove(wallet.key())
		self.set_labels.remove(wallet.label)
		self.set_addr.remove(wallet.addr_lower)


	def _add_wallet(self, wallet: Wallet):
		"""Adds wallet into the list and sets"""
		assert isinstance(wallet, Wallet), "I can add only wallet and that's not wallet. Tell the devs"
		if not wallet.addr:								# if no addr
			self.update_wallet(wallet, True)			# get it

		self.wallets.append(wallet)				# add to the list
		self._add_to_sets(wallet)				# add to the sets

	def _delete_wallet(self, index_or_obj):
		"""
		Deletes wallet from list and sets by its Index in the list or Wallet obj
		:param index_or_obj: wallet Index in the list OR wallet Obj in the list
		"""
		if isinstance(index_or_obj, Wallet):  # if it's wallet - get it's index
			for i in range(len(self.wallets)):
				if index_or_obj is self.wallets[i]:
					index_or_obj = i
					break
		assert isinstance(index_or_obj, int), "It's not wallet or index, I don't work with it. Tell the devs"

		wallet = self.wallets.pop(index_or_obj)  # del from the list
		self._delete_from_sets(wallet)  # del from the sets
		print(texts.deleted_successfully, wallet.addr)  # print about success
		del wallet

	def _delete_first_N(self, line):
		"""Deletes N first wallets
		:param line: str that starts on "first..." """
		if line == "first":  # if first - delete first
			self._delete_wallet(0)
		else:  # if more:
			amount = int(line.split(" ")[1])  # parse amount
			assert amount <= len(self.wallets), texts.del_out_of_index
			for _ in range(amount):  # delete them
				self._delete_wallet(0)

	def _delete_last_N(self, line):
		"""Deletes N last wallets
		:param line: str that starts on "last..." """
		if line == "last":  # if last - delete it
			self._delete_wallet(len(self.wallets) - 1)
		else:  # if more:
			amount = int(line.split(" ")[1])  	# parse amount
			assert amount <= len(self.wallets), texts.del_out_of_index
			for _ in range(amount):  			# delete them
				self._delete_wallet(len(self.wallets) - 1)

	def _check_last_block(self) -> bool:
		"""
		Checks that the last block is exist.
		If it doesn't exist - tries to update it
		:return: True or False
		"""
		if self.last_block is not None:  # exist - Ok, tell it
			return True
		else:  # No?
			print("No info about the last block, updating...", sep=" ")
			self.update_last_block()  # Try to update

			if self.last_block is not None:  # if not Ok - tell it
				print(texts.success)
				return True
			else:
				print(texts.fail)  # no? - So sad...
				return False

	def _daemon_update_last_block(self):
		"""Daemon updates block even N secs"""
		while True:
			self.update_last_block()  # update
			time.sleep(settings.update_block_every)  # sleep
			logs.pr_daemon(f"Daemon, updated the last block, current block is {self.last_block['number']}")

	def _daemon_update_gas(self):
		"""Daemon updates gas price & max priority every N secs. Very important info, change with care"""
		while True:		# no change int !! That's wei, so Ok. And web3 doesn't work with float.
			Manager.network_gas_price = int(self.w3.eth.gas_price * settings.gas_multiplier)
			Manager.network_max_priority = int(self.w3.eth.max_priority_fee * settings.priority_multiplier)

			min_gas = Web3.toWei(settings.min_gas, "gwei")				# get min gas from settings
			if Manager.network_gas_price < min_gas:						# if gas less than min... you got
				Manager.gas_price = min_gas
			else:
				Manager.gas_price = Manager.network_gas_price

			min_priority = Web3.toWei(settings.min_priority, "gwei")	# get min prior from settings...
			if Manager.network_max_priority < min_priority:
				Manager.max_priority = min_priority
			else:
				Manager.max_priority = Manager.network_max_priority

			time.sleep(settings.update_gas_every)

	def _save_wallets(self):
		assist.save_data(self.wallets, settings.folder, settings.saved_wallets)

	def _load_wallets(self):
		print(texts.loading_wallets, end=" ")  	# Start
		loaded_data = assist.load_data(settings.folder, settings.saved_wallets)
		if loaded_data is None:
			print(texts.no_wallets_to_load)	# End - Tell no wallets to load
		else:
			self.wallets = loaded_data
			print(texts.success)  						# End - Success

###################################################################################################
# Default methods #################################################################################
###################################################################################################

	def try_add_wallet(self):
		"""Parses line and adds a wallet by private key"""
		max_ = settings.max_wallets
		created = len(self.wallets)
		while True:
			assert created < max_, texts.error_max_wallet_created.format(created, max_)

			print(texts.input_private_key)
			key = input().strip().lower()
			if not key:
				print(texts.exited)
				break
			# If starts not with 0x or length not 66 symbols - tell about mistake
			if not key.startswith("0x") or len(key) != settings.private_key_length:
				print(texts.error_not_private_key)
				continue
			elif key in self.set_keys:  			# If exits - tell the label of the wallet
				label = "Hmmm... unknown.. tell the devs"
				for wallet in self.wallets:  		# find this wallet
					if key == wallet.key():  			# if this wallet - same what the user wrote
						label = wallet.label  			# get the label
						break  							# stop and write it
				print(texts.error_wallet_exist_with_label.format(label))
			else:  	# If OK - add the wallet
				wallet = Wallet(key)  					# create Wallet

				if threads.can_create_daemon():
					thread = threads.start_todo(self.update_wallet, True, wallet, True)
					label = self.ask_label()			# ask label
					thread.join()
				else:
					label = self.ask_label()  			# ask label
					self.update_wallet(wallet, True)  	# update info

				wallet.label = label		# first wait for daemon to finish, then change the label
				self._add_wallet(wallet)				# add wallet
				print(texts.added_wallet.format(wallet))

	def generate_wallets(self, number):
		max_ = settings.max_wallets
		created = len(self.wallets)
		assert created < max_, texts.error_max_wallet_created.format(created, max_)

		allowed = max_ - created		# check if allowed
		if number < 1 or number > allowed or number > settings.max_generate_addr:
			if allowed > settings.max_generate_addr:
				max_can_gen = settings.max_generate_addr
			else:
				max_can_gen = allowed
			print(texts.error_wrong_generate_number.format(allowed, created, max_, max_can_gen, number))
			print(texts.exited)
		else:							# get the list with new generated wallets
			new_generated_wallets = assist.generate_wallets(self.w3,
															self.set_labels.copy(),
															self.set_keys.copy(),
															number)
			# add it to our list
			[self._add_wallet(wallet) for wallet in new_generated_wallets]

			[print(wallet.addr, wallet.key()) for wallet in new_generated_wallets]
			print("Generated wallets:", len(new_generated_wallets))				# print generated wallets info

	def try_delete_wallet(self):
		""" Realisation of deleting wallets -> certain wallet, last, last N or all
		If change - be careful with .lower method !!
		"""
		assert self.wallets, texts.no_wallets

		print(texts.instruction_to_delete_wallet)			# instruction
		addr = self.print_and_ask(text_before="List of existed wallets:")
		if not addr:
			print(texts.exited)
			return

		# Processing the input
		if addr.startswith("last"):		# if last - delete last
			self._delete_last_N(addr)
		elif addr.startswith("first"):	# if first - delete first
			self._delete_first_N(addr)
		else:									# else get wallet and
			index = self.get_wallet_index_by_text(addr)  	# delete it
			self._delete_wallet(index)

	def delete_all(self):
		"""Deletes all wallets, use with careful"""
		self.wallets.clear()
		self.set_addr.clear()
		self.set_labels.clear()
		self.set_keys.clear()

	def try_send_transaction(self):
		assert self.wallets, texts.no_wallets

		try:
			print("All wallets: ")  					# instruction
			self.print_wallets()  						# print wallets

			print("From which send:")
			sender = self.get_wallet_by_text(input())

			daemon = threads.start_todo(self.update_wallet, True, sender)
			print("To which send:")
			receiver = self.get_wallet_by_text(input())

			print("Write amount:")
			amount = self.w3.toWei(input(), "ether")

			daemon.join()
			txs_list: list = trans.transaction_sender(self.w3, sender, receiver, amount)

			[Manager.all_txs.append(tx) for tx in txs_list if tx not in Manager.all_txs]		# add tx
			[print(tx) for tx in txs_list]														# print
		except Exception as e:
			print(texts.error_something_wrong.format(e))

	def try_send_to_all(self):
		assert self.wallets, texts.no_wallets

		sender_raw = self.print_and_ask(text_after="From which wallet to send?")		# get input
		sender_index = self.get_wallet_index_by_text(sender_raw)				# get sender index

		receivers = self.wallets.copy()											# copy all list
		sender = receivers.pop(sender_index)									# get sender and delete from list
		daemon = threads.start_todo(self.update_wallet, True, sender)			# start daemon to update sender info

		amount = self.w3.toWei(input("How much send to each: "), "ether")

		if trans.print_price_and_confirm(self.chain_id, value=amount, receivers=receivers):
			daemon.join()
			txs = trans.transaction_sender(self.w3, sender, receivers, amount)	# send txs
			[Manager.all_txs.append(tx) for tx in txs if tx not in Manager.all_txs]	# add to lis
			[print(tx) for tx in txs]

	def update_wallets(self):
		assert self.wallets, texts.no_wallets

		list_daemons = list()

		for wallet in self.wallets:  			# for each wallet
			if threads.can_create_daemon():  	# if allowed thread creating - start a new thread
				thread = threads.start_todo(self.update_wallet, True, wallet, True)
				list_daemons.append(thread)  	# add thread to the list
			else:
				time.sleep(settings.wait_to_create_daemon_again)

		[daemon.join() for daemon in list_daemons if daemon.is_alive()]  	# wait will all threads finish

	def print_block_info(self, block_number=None):
		"""
		Prints info about transferred block
		or the last block if block_number is None
		:param block_number: str or int of the block
		:return: nothing
		"""
		# We have to know info about the last block
		if not self._check_last_block():
			print(texts.error_no_info_about_last_block)
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
				print(texts.error_block_doesnt_exist_yet)
				return
			else:
				block = self.w3.eth.get_block(block_number)

		for k, v in block.items():					# get key and value
			print(k, end=" >>> ")						# print key, no \n

			if isinstance(v, bytes):								# if Value is bytes
				print(self.w3.toHex(v))		# decode Value and print
			elif isinstance(v, list):			# if Value is list
				if not v:						# list empty - print \n
					print()
				else:							# not empty
					for el in v:				# decode and print all elements
						print(self.w3.toHex(el))
			else:								# if Value not list and not bytes - print it
				print(v)

###################################################################################################
# Assist methods ##################################################################################
###################################################################################################

	def print_wallets(self):
		"""Prints wallets with its index"""
		assert self.wallets, texts.no_wallets
		assist.print_wallets(self.wallets)

	def print_all_info(self):
		"""Prints wallets with its index and TXs list"""
		assert self.wallets, texts.no_wallets
		assist.print_all_info(self.wallets)

	def print_all_txs(self):
		"""Prints all TXs with current network (chain_id)"""
		assert Manager.all_txs, texts.no_txs
		assist.print_all_txs(self.chain_id)

	def print_and_ask(self, text_before=None, text_after=None) -> str:
		"""Prints wallets and ask to choose the wallet
		:param text_before: str, prints text before wallets list
		:param text_after: str, prints text after wallets list
		:return: user's input"""
		if text_before is not None:
			print(text_before)			# print text_before is there's

		self.print_wallets()			# prints wallets

		if text_after is not None:
			print(text_after)			# print text_after is there's
		return input().strip().lower()

	def update_wallet(self, wallet, update_tx=False):
		"""Updates wallet balance & nonce, adds addr if wallet doesn't have it.
		Updates TXs in the wallet list which doesn't have status (Success/Fail)"""
		assist.update_wallet(self.w3, wallet, self.set_labels, update_tx)

	def delete_txs_history(self):
		assist.delete_txs_history(self.wallets)

	def print_txs_for_wallet(self):
		"""Prints TXs for selected wallet in current blockchain"""
		text = self.print_and_ask(text_after="Choose the acc:")				# prints wallets + ask to choose
		wallet = self.get_wallet_by_text(text)							# gets wallet from str
		assist.print_txs_for_wallet(self.chain_id, wallet)		# prints txs for that wallet in the network

	def get_wallet_by_text(self, addr_or_number) -> Wallet:
		"""Returns wallet by address or number (starts from 1)
		:param addr_or_number: should be lower"""
		index = self.get_wallet_index_by_text(addr_or_number)
		return self.wallets[index]

	def get_wallet_index_by_text(self, text) -> int:
		"""Returns index of the wallet in the list with received text (addr or number)"""
		return assist.get_wallet_index_from_input(self.wallets, self.set_addr, self.set_labels, text)

	def ask_label(self) -> str:
		"""Asks label and checks uniqueness"""
		return assist.ask_label(self.set_labels.copy())

	def update_last_block(self):
		self.last_block = self.w3.eth.get_block("latest")

	def connection_status(self):
		if self.w3.isConnected():
			is_connected = texts.success
		else:
			is_connected = texts.fail
		print("Connection:", is_connected)

###################################################################################################
# Finish ##########################################################################################
###################################################################################################

	def finish_work(self):
		save_txs()					# Save TXs
		self.delete_txs_history()	# Delete tx_list +
		self._save_wallets()		# Save wallets