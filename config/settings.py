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


# chains ID
chainId_ETH = 1
chainId_BNB = 55
chainId_MATIC = 137
chainId_AVAX = 43114
chainId_FANTOM = 250
chainId_OPTIMISM = 10
chainId_ARBITRUM = 42161
chainId_testnet_ETH_Goerli = 5
chainId_testnet_BNB = 97
