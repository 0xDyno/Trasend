from web3 import Web3
import os
import pickle
from config import settings

"""Created class to manage wallets"""


def is_web3(connection):
	if type(connection) is not Web3:
		raise Exception("Can't create Manager because got wrong Connection type. "
						f"Should be {Web3} object, got: {type(connection)}")


class Manager:
	__singleton = None
	connection: Web3 = None
	list_with_wallets = list()

	def __new__(cls, *args, **kwargs):
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)

			# Loading addresses
			cls.__singleton.load_list_with_wallets()
			cls.__singleton.update_wallets()

		return cls.__singleton

	def __del__(self):
		# Saving addresses
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
		pass

	def delete_wallet(self):
		pass

	def generate_wallets(self, number=1):
		"""Later realisation"""
		pass

	def load_list_with_wallets(self):
		# Do if folder and file exist
		if os.path.exists(settings.folder) and os.path.isfile(settings.saved_wallets):

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