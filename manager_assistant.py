from web3 import Web3
from datetime import date
from config import settings
from cryptography.fernet import Fernet
import os


def is_web3(connection):
	"""
	Checks the connection is Web3
	"""
	if not isinstance(connection, Web3):
		raise TypeError("Can't create Manager because got wrong Connection type. "
						f"Should be {Web3} object, got: {connection}")


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