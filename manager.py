import threading

from web3 import (
	Web3,
	Account
)
from config import text, settings
from wallet import Wallet
from random import random
from threading import *
from time import time, sleep
import os, pickle


def is_web3(connection):
	if isinstance(type(connection), Web3):
		raise TypeError("Can't create Manager because got wrong Connection type. "
						f"Should be {Web3} object, got: {type(connection)}")

"""Class Manager to manage wallets"""


class Manager:
	__singleton = None
	web3: Web3 = None
	list_with_wallets = list()

	# added from list_with_wallets when __init__
	set_with_private_keys = set()
	set_with_labels = set()
	set_with_addresses = set()

	# other params
	last_block = None			# updates every 12 secs

	def new_connection(self, connection):
		is_web3(connection)
		self.web3 = connection

	def __new__(cls, *args, **kwargs):
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)

		return cls.__singleton

	def __del__(self):
		Manager.__singleton = None

	def __init__(self, connection):
		"""
		 If object creates first time - it will ask for Web3 object
		 If second time - it will use connection from 1st time
		 To change connection - use obj.new_connection(new_Web3)
		"""
		if self.web3 is None:
			is_web3(connection)
			self.web3 = connection

			# Get status of the connection
			print(f"Connection status: {self.web3.isConnected()}")

			# Loading addresses
			self.__singleton.load_list_with_wallets()

			# Init sets if there are wallets
			if not self.__singleton.list_with_wallets:
				print(text.new_text_no_wallets_to_init)
			else:
				self.__singleton.update_wallets()
				self.__singleton.initialize_sets()

			# Start a demon to regularly update info (last block)
			self.is_main_finished = False
			self.daemon_to_update_last_block = None
			self.start_daemon_to_update_last_block()
		else:
			print(f"Connection status: {self.web3.isConnected()}")

	def add_wallet(self):
		"""Checking one by one has the same speed as using a batch.
		Now I implement import one by one. Later I can add import batch of private keys.
		"""
		while True:
			try:
				print(text.add_input_private_key)
				key = input().strip().lower()
				if not key or key == "exit":
					break

				if not key.startswith("0x"):  					# If not starts with 0x - tell about mistake
					print(text.add_error_wrong_first_symbols)
					continue
				elif len(key) != settings.private_key_length:  	# If not 66 symbols - tell about mistake
					print(text.add_error_wrong_length)
					continue
				elif key in self.set_with_private_keys:  		# If exits - tell the label of the wallet
					label = "Unknown.. tell the devs"
					for wallet in self.list_with_wallets:  		# find this wallet
						if key == wallet.key():  	# if this wallet - same what the user wrote
							label = wallet.label  				# get the label
							break  								# stop and write it
					print(f"Error, the key is already added to the system with the label \"{label}\"")
				else:  	# If OK - add the wallet
					label = self.ask_label()  		# get label
					wallet = Wallet(key, label)  	# create Wallet
					self.update_wallet(wallet)  	# update info

					self.list_with_wallets.append(wallet)  	# add wallet to the list
					self.add_to_sets(wallet)  				# add data to sets
					print(f"Successfully added the wallet: {wallet.get_all_info()}")
			except Exception as e:
				# raise Exception(e)
				print(f"Something wrong, mistake: {e}\nTry again.")

	def delete_wallet(self):
		""" Realisation of deleting wallets -> certain wallet, last, last N or all """
		while True:
			try:
				if not self.list_with_wallets:					# If no wallets
					print(text.del_no_wallets)					# tell about it
					return										# and return

				print(text.del_instruction_to_delete_wallet)	# instruction
				self.print_wallets()  							# print wallets
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
						last_index = len(self.list_with_wallets) - 1	# - get last index
						self.delete_wallet_by_index(last_index)			# - delete it
				elif process_line == "all":
					for i in range(len(self.list_with_wallets)):		# delete all
						self.delete_wallet_by_index()
				else:
					index = self.get_wallet_index_from_list(line)		# else get wallet index
					self.delete_wallet_by_index(index)					# delete it
			except Exception as e:
				print("Something went wrong:", e, end="\n\n")

	def generate_wallets(self, number=1):
		new_generated_wallets = list()
		if number > 100:
			print(text.error_more_than_100)
		else:
			print("Started the generation. Created: ", end="")
			for i in range(number):
				is_created = False
				while not is_created:
					key = self.web3.toHex(self.web3.eth.account.create().key)
					if key not in self.set_with_private_keys:
						label = self.generate_label()
						wallet = Wallet(key, label)

						self.list_with_wallets.append(wallet)
						self.update_wallet(wallet)
						self.add_to_sets(wallet)

						new_generated_wallets.append(wallet)
						is_created = True

				print(i+1, end="")			# just "progress bar", will write number of created acc
				if i+1 < number:			# and add .. between them if it's not the last one
					print("..", end="")
			print()							# end of the "progress bar", xD

			print("Generated wallets:")
			for wallet in new_generated_wallets:
				print(wallet.address, wallet.key())


	def update_wallets(self):
		if self.list_with_wallets:
			print(text.upd_text_updating_wallets, end=" ")
			for wallet in self.list_with_wallets:
				self.update_wallet(wallet)
			print(text.success)
		else:
			print(text.upd_text_no_wallets_to_update)

	def update_wallet(self, wallet):
		if isinstance(wallet, Wallet):
			if not wallet.address:  						  # if the wallet doesn't have address
				key = wallet.key()														# parse it
				wallet.address = Account.privateKeyToAccount(key).address				# and add

			wallet.balance_in_wei = self.web3.eth.get_balance(wallet.address)		# update balance
			wallet.nonce = self.web3.eth.get_transaction_count(wallet.address)	# update nonce
		else:
			print(text.upd_error_not_wallet)

	def delete_wallet_by_index(self, index=0):			# if no index - will delete first one
		wallet = self.list_with_wallets.pop(index)  	# del from the list
		self.delete_from_sets(wallet)					# del from the sets
		print(text.del_successfully_deleted, wallet.address)		# print about success
		del wallet

	def initialize_sets(self):
		print(text.sets_text_init_sets, end=" ")
		for wallet in self.list_with_wallets:
			self.add_to_sets(wallet)
		print(text.success)

	def add_to_sets(self, wallet):
		"""Adds new wallet to sets if there's no such wallet.
		If there's same data - throws Exception"""
		key = wallet.key()
		label = wallet.label
		address = wallet.address

		# if any field in the set - throw error. Else - add new wallet
		if key in self.set_with_private_keys or \
			label in self.set_with_labels or \
			address in self.set_with_addresses:

			raise Exception(text.error_add_to_set)
		else:
			self.set_with_private_keys.add(key)
			self.set_with_labels.add(label)
			self.set_with_addresses.add(address)

	def delete_from_sets(self, wallet):
		""" Deletes wallet from the sets if every field is in sets. Otherwise, throws Exception """
		key = wallet.key()
		label = wallet.label
		address = wallet.address

		if key in self.set_with_private_keys and \
			label in self.set_with_labels and \
			address in self.set_with_addresses:

			self.set_with_private_keys.remove(key)
			self.set_with_labels.remove(label)
			self.set_with_addresses.remove(address)
		else:
			raise Exception(text.error_delete_from_set)

	def print_wallets(self):
		if not self.list_with_wallets:
			print(text.text_no_wallets)
		else:
			length = len(self.list_with_wallets)
			for i in range(length):  											# print all addresses
				print(f"{i + 1}. {self.list_with_wallets[i].get_all_info()}")  	# with its index

	def ask_label(self):
		while True:
			label = input(text.add_ask_label).strip()
			if not label:								# If empty - generate 5 digits number
				return self.generate_label()

			if label.lower() == "exit":  				# If not empty - check if "exit"
				raise Exception("Exited while tried to write the label")

			if label in self.set_with_labels:  			# Then check if the label exist
				print("This label is exist. Try another")
			else:  										# if not - return it
				return label

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

	def generate_label(self):
		while True:
			number = int(random() * 10**5)
			if number < 10000:
				pass
			else:
				label = str(number)
				if label not in self.set_with_labels:
					return label


	def get_wallet_index_from_list(self, input_: str = None) -> int:
		""" Get wallet index from list with received input or parse
				:param input_: text (address or number of the wallet)
				:return: Index of selected Wallet in the list
				"""

		if not self.list_with_wallets:  		# If no wallets - raise error
			raise Exception(text.text_no_wallets)
		if input_ is None:						# if no argument - ask the wallet
			print(text.text_enter_wallet_or_number)
			self.print_wallets()
			input_ = input()
		if input_.isnumeric():  							# get number if it's number
			number = int(input_)
			# if number = 0 or Bigger, than # of wallets in the list
			if number == 0 or number > len(self.list_with_wallets):
				raise Exception("Wrong number")				# throw error
			return number - 1								# if not - return Index

		elif not input_.startswith("0x") or len(input_) != settings.address_length:
			raise Exception(text.error_not_number_or_address)
		else:
			if input_ not in self.set_with_addresses:  				# if there's no such wallet
				raise Exception(text.error_no_such_address) 		# throw error

			else:
				for index in range(len(self.list_with_wallets)):	# else find its Index
					if self.list_with_wallets[index].address == input_:
						return index								# end return

	def update_last_block(self):
		self.last_block = self.web3.eth.get_block("latest")

	def check_last_block(self) -> bool:
		"""
		Checks that the last block is exist.
		If it doesn't exist - tries to update it

		:return: True or False
		"""
		if self.last_block is not None:
			return True
		else:
			print("No info about the last block, updating... ")
			self.update_last_block()

			if self.last_block is None:
				return False
			else:
				return True

	def start_daemon_to_update_last_block(self):
		# Update the last block forever every N seconds
		def work_for_daemon():
			while True:
				if self.is_main_finished:
					break

				self.update_last_block()

				if settings.print_tech_info:
					print("Daemon, updated the last block, current block is", self.last_block["number"])

				sleep(settings.ETH_block_time)

		# create a Daemon to do work in work_for_daemon()
		self.daemon_to_update_last_block = Thread(target=work_for_daemon)
		self.daemon_to_update_last_block.start()

# Import-Export methods

	def load_list_with_wallets(self):
		# Printing info - beginning
		print(text.new_text_load_the_wallets, end=" ")

		# Work - Do if folder and file exist
		if os.path.isdir(settings.folder) and os.path.isfile(settings.saved_wallets):

			with open(settings.saved_wallets, "rb") as r:
				get_bytes = r.read()
				# Separate string by separator and add to the list
				list_of_bytes = get_bytes.split(settings.separator.encode())

			for element in list_of_bytes:
				if not element:  # pass if empty
					continue

				address = pickle.loads(element)
				self.list_with_wallets.append(address)

		# Printing info - end
		if not self.list_with_wallets:
			print(text.new_text_not_wallets_to_load)
		else:
			print(text.success)

	def save_wallets_list(self):
		if not os.path.exists(settings.folder):  	# Checking if the path exist
			os.mkdir(settings.folder)

		if not self.list_with_wallets:  			# If no wallets - clear file
			w = open(settings.saved_wallets, "w")
			w.close()
		else:
			with open(settings.saved_wallets, "wb") as w:  	# Save to the file

				for wallet in self.list_with_wallets:  		# For each wallet in the list
					w.write(pickle.dumps(wallet))  			# save it and
					w.write(settings.separator.encode())  	# add separator

# Finish

	def finish_work(self):
		self.save_wallets_list()

		# Finish the demon
		self.is_main_finished = True