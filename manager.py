from web3 import Web3, Account
from eth_account.signers.local import LocalAccount
from config import settings
from wallet import Wallet
from random import random
import os
import pickle


def is_web3(connection):
	if isinstance(type(connection), Web3):
		raise TypeError("Can't create Manager because got wrong Connection type. "
						f"Should be {Web3} object, got: {type(connection)}")


"""Class Manager to manage wallets"""


class Manager:
	__singleton = None
	connection: Web3 = None
	list_with_wallets = list()

	# added from list_with_wallets when __init__
	set_with_private_keys = set()
	set_with_labels = set()
	set_with_addresses = set()

	def new_connection(self, connection):
		is_web3(connection)
		self.connection = connection

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
		if self.connection is None:
			is_web3(connection)
			self.connection = connection

			# Loading addresses
			self.__singleton.load_list_with_wallets()

			if not self.__singleton.list_with_wallets:  		# if no wallets
				print(settings.new_text_no_wallets_to_init)  	# tell it
			else:  	# else init
				# Update info & initialisation
				self.__singleton.update_wallets()
				self.__singleton.initialize_sets()

	def add_wallet(self):
		"""Checking one by one has the same speed as using a batch.
		Now I implement import one by one. Later I can add import batch of private keys.
		"""
		while True:
			try:
				print(settings.add_input_private_key)
				key = input().strip().lower()
				if not key or key == "exit":
					break

				if not key.startswith("0x"):  					# If not starts with 0x - tell about mistake
					print(settings.add_error_wrong_first_symbols)
					continue
				elif len(key) != settings.private_key_length:  	# If not 66 symbols - tell about mistake
					print(settings.add_error_wrong_length)
					continue
				elif key in self.set_with_private_keys:  		# If exits - tell the label of the wallet
					label = "Unknown.. tell the devs"
					for wallet in self.list_with_wallets:  		# find this wallet
						if key == wallet.get_private_key():  	# if this wallet - same what the user wrote
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
		"""
		Realisation of deleting only one wallet per time for now, by number or address
		"""
		if not self.list_with_wallets:  # If no wallets - tell about it and return
			print(settings.del_no_wallets)
			return

		while True:
			try:
				print(settings.del_instruction_to_delete_wallet)  # instruction
				self.print_wallets()  	# print wallets
				print("---------------------")

				line = input().strip()
				if not line or line.lower() == "exit":
					break

				# Processing the input
				if line.lower().startswith("last"):
					try:
						how_many_delete = int(line.split(" ")[1])
						for i in range(how_many_delete):
							self.delete_wallet_by_index(len(self.list_with_wallets)-1)
					except Exception:
						print("Wrong format, try again")
				elif line.isnumeric():  								# if it's number
					number = int(line)
					if number > len(self.list_with_wallets):  		# if number bigger than # of wallets
						print(settings.del_wrong_number)  			# tell about wrong number
					else:
						self.delete_wallet_by_index(number - 1)  	# delete
				elif line.startswith("0x") and len(line) == settings.address_length:
					if line not in self.set_with_addresses:  		# if it's address - check if we have such
						print(settings.del_error_no_such_address)  	# if not - tell it
					else:
						for index in range(len(self.list_with_wallets)):  	# else find its index
							if self.list_with_wallets[index].address == line:
								self.delete_wallet_by_index(index)  		# delete
								break
				else:
					print(settings.del_error_not_number_or_address)

			except Exception as e:
				print("Something went wrong, mistake:", e)

	def generate_wallets(self, number=1):
		new_generated_wallets = list()
		if number > 100:
			print(settings.error_more_than_100)
		else:
			print("Started the generation.")
			for i in range(number):
				is_created = False
				while not is_created:
					key = self.connection.toHex(self.connection.eth.account.create().key)
					if key not in self.set_with_private_keys:
						label = self.generate_label()
						wallet = Wallet(key, label)

						self.list_with_wallets.append(wallet)
						self.update_wallet(wallet)
						self.add_to_sets(wallet)

						new_generated_wallets.append(wallet)
						is_created = True
			print("Generated wallets:")
			for wallet in new_generated_wallets:
				print(wallet.address)


	def update_wallets(self):
		if self.list_with_wallets:
			print(settings.upd_text_updating_wallets)
			for wallet in self.list_with_wallets:
				self.update_wallet(wallet)
		else:
			print(settings.upd_text_no_wallets_to_update)

	def update_wallet(self, wallet):
		if isinstance(wallet, Wallet):
			if not wallet.address:  						  # if the wallet doesn't have address
				key = wallet.get_private_key()											# parse it
				wallet.address = Account.privateKeyToAccount(key).address				# and add

			wallet.balance_in_wei = self.connection.eth.get_balance(wallet.address)		# update balance
			wallet.nonce = self.connection.eth.get_transaction_count(wallet.address)	# update nonce
		else:
			print(settings.upd_error_not_wallet)

	def delete_wallet_by_index(self, index):
		wallet = self.list_with_wallets.pop(index)  	# del from the list
		self.delete_from_sets(wallet)					# del from the sets
		del wallet
		print(settings.del_successfully_deleted)		# print about success

	def initialize_sets(self):
		print(settings.sets_text_init_sets)
		for wallet in self.list_with_wallets:
			self.add_to_sets(wallet)

	def add_to_sets(self, wallet):
		key = wallet.get_private_key()
		label = wallet.label
		address = wallet.address

		if key in self.set_with_private_keys or \
			label in self.set_with_labels or \
			address in self.set_with_addresses:
			raise Exception(settings.error_add_to_set)
		else:
			self.set_with_private_keys.add(key)
			self.set_with_labels.add(label)
			self.set_with_addresses.add(address)

	def delete_from_sets(self, wallet):
		key = wallet.get_private_key()
		label = wallet.label
		address = wallet.address

		if key in self.set_with_private_keys and \
			label in self.set_with_labels and \
			address in self.set_with_addresses:

			self.set_with_private_keys.remove(key)
			self.set_with_labels.remove(label)
			self.set_with_addresses.remove(address)
		else:
			raise Exception(settings.error_delete_from_set)

	def print_wallets(self):
		if not self.list_with_wallets:
			print(settings.text_no_wallets_to_print)
		else:
			length = len(self.list_with_wallets)
			for i in range(length):  											# print all addresses
				print(f"{i + 1}. {self.list_with_wallets[i].get_all_info()}")  	# with its index

	def ask_label(self):
		while True:
			label = input(settings.add_ask_label).strip()
			if not label:								# If empty - generate 5 digits number
				return self.generate_label()

			if label.lower() == "exit":  				# If not empty - check if "exit"
				raise Exception("Exited while tried to write the label")

			if label in self.set_with_labels:  			# Then check if the label exist
				print("This label is exist. Try another")
			else:  										# if not - return it
				return label

	def generate_label(self):
		while True:
			number = int(random() * 10**5)
			if number < 10000:
				pass
			else:
				label = str(number)
				if label not in self.set_with_labels:
					return label

	# Import-Export methods

	def load_list_with_wallets(self):
		print(settings.new_text_load_the_wallets)
		# Do if folder and file exist
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

	def save_wallets_list(self):
		if not os.path.exists(settings.folder):  # Checking if the path exist
			os.mkdir(settings.folder)

		if not self.list_with_wallets:  # If no wallets - clear file
			w = open(settings.saved_wallets, "w")
			w.close()
		else:
			with open(settings.saved_wallets, "wb") as w:  # Save to the file

				for wallet in self.list_with_wallets:  # For each wallet in the list
					w.write(pickle.dumps(wallet))  # save it and
					w.write(settings.separator.encode())  # add separator
