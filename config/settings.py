"""Static""" 			#################################################
private_key_length = 66
address_length = 42
gas_for_native = 21000


""" For Manager """		#################################################
folder = "private/"
saved_wallets = folder + "saved_wallets"
saved_txs = folder + "saved_txs"
crypto_key = folder + "key"
max_generate_addr = 100

"""Daemons"""			#################################################
print_daemons_info = False			# prints info from daemons
update_block_every = 3				# 12 secs for ETH
update_gas_every = 3				#
max_threads_per_time = 30			# not more than N threads
wait_to_create_daemon_again = 0.5	# If no free place to create a daemon - it will wait that time before try again


"""Transactions"""		#################################################
print_trans_info = True				# prints info when does a transaction
multiplier = 2					# to multiply gas price (paid only for used gwei, other returns)
multiplier_priority = 1.5		# to multiply priority (will be paid full price 100%)
chain_explorers = {
	1: "https://etherscan.io/tx/",
	5: "https://goerli.etherscan.io/tx/"
}
chain_default_coin = {
	1: "ETH",
	5: "ETH"
}
chain_name = {
	1: "ETH mainnet",
	5: "Goerli ETH testnet"
}