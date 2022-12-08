"""Static""" 			#################################################

private_key_length = 66
address_length = 42


""" For Manager """		#################################################

separator = " | "
folder = "saved/"
file_name = "saved_addresses.pickle"
saved_wallets = folder + file_name
print_tech_info = False					# prints additionally info

"""Daemons"""			#################################################
ETH_block_time = 3		# 12 secs for ETH


"""Transactions"""		#################################################

multiplier = 1.5				# to multiply gas price and priority
chainId_ETH = 1
chainId_t_ETH_Goerli = 5