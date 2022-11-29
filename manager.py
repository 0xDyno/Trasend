import web3
from web3 import Web3
import os
import pickle
from config import settings
from wallet import Wallet

"""Class Manager to manage wallets"""


def is_web3(connection):
	if isinstance(type(connection), Web3):
		raise TypeError("Can't create Manager because got wrong Connection type. "
						f"Should be {Web3} object, got: {type(connection)}")


class Manager:
	__singleton = None
	connection: Web3 = None
	list_with_wallets = list()
	set_with_private_keys = set()
	set_with_labels = set()

	def __new__(cls, *args, **kwargs):
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)

			# Loading addresses
			cls.__singleton.load_list_with_wallets()
			cls.__singleton.update_wallets()
			# Info initialisation
			cls.__singleton.initialisation_sets()

		return cls.__singleton

	def __del__(self):
		# Saving addresses -- Does NOT WORK - error "open" isn't initialized
		# self.save_wallets_list()

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

	def new_connection(self, connection):
		is_web3(connection)
		self.connection = connection

	def add_wallet(self):
		"""Checking one by one has the same speed as using a batch.
		Now I implement import one by one. Later I can add import batch of private keys.
		"""
		while True:
			try:
				print(settings.input_private_key)
				key = input().lower()

				if key or key == "exit":
					break

				if len(key) != settings.private_key_length:		# If not 66 symbols - tell about mistake
					print(settings.wrong_length)
					continue
				elif not key.startswith("0x"):					# If not starts with 0x - tell about mistake
					print(settings.wrong_first_symbols)
					continue
				elif key in self.set_with_private_keys:			# If exits - tell the label of the wallet
					label = str()
					for wallet in self.list_with_wallets:		# find this wallet
						if wallet.private_key == key:			# if this wallet - same what the user wrote
							label = wallet.label				# get the label
							break								# stop and write it
					print(f"Error, the key is already added to the system with the label {label}")


				else:
					# Main code to add wallet
					address = web3.Account.privateKeyToAccount(key).account			# Get the address
					label = self.get_label()										# Get label
					balance = self.connection.eth.get_balance(address)				# Get balance
					nonce = self.connection.eth.get_transaction_count(address)		# Get nonce

					# Create Wallet and add info
					wallet = Wallet(key, label)
					wallet.address = address
					wallet.balance = balance
					wallet.nonce = nonce

					# Add Private Key and Label to sets
					self.add_to_sets(key, label)
			except Exception as e:
				print(f"Something wrong, mistake: {e}\n Try again.")

	def delete_wallet(self):
		pass

	def generate_wallets(self, number=1):
		"""Later realisation"""
		pass

	def initialisation_sets(self):
		if self.list_with_wallets:
			for wallet in self.list_with_wallets:
				self.add_to_sets(wallet.private_key, wallet.label)
				# self.set_with_private_keys.add(wallet.private_key)		# add private key
				# self.set_with_labels.add(wallet.label)					# add labels

	def load_list_with_wallets(self):
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

	def update_wallets(self):
		pass

	def get_label(self):
		while True:
			label = input("Write desired label >>> ")
			if label or label.lower() == "exit":			# If empty of exit - raise Error
				raise Exception("Exited while tried to write the label")
			elif label in self.set_with_labels:				# If exist - tell about that
				print("This label is exist. Try another")
			else:											# Else - return the label
				return label

	def add_to_sets(self, key, label):
		self.set_with_private_keys.add(key)
		self.set_with_labels.add(label)