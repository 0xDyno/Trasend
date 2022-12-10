"""Static""" 			#################################################

private_key_length = 66
address_length = 42


""" For Manager """		#################################################

separator = " | "
folder = "private/"
saved_wallets = folder + "saved_data"
crypto_key = folder + "key"

"""Daemons"""			#################################################
update_block_every = 3				# 12 secs for ETH
print_daemons_info = False			# prints info from daemons
print_trans_info = True				# prints info when does a transaction


"""Transactions"""		#################################################

multiplier = 1.2				# to multiply gas price and priority