"""Static""" 			#################################################
private_key_length = 66
address_length = 42


""" For Manager """		#################################################
folder = "private/"
saved_wallets = folder + "saved_wallets"
saved_txs = folder + "saved_txs"
crypto_key = folder + "key"
max_generate_addr = 100

"""Daemons"""			#################################################
update_block_every = 3				# 12 secs for ETH
print_daemons_info = False			# prints info from daemons
print_trans_info = False			# prints info when does a transaction
max_threads_per_time = 30			# not more than N threads
wait_to_create_daemon_again = 0.5	# If no free place to create a daemon - it will wait that time before try again


"""Transactions"""		#################################################
multiplier = 1.2					# to multiply gas price and priority
chain_explorers = {
	1: "https://etherscan.io/tx/",
	5: "https://goerli.etherscan.io/tx/"
}
chain_default_token = {
	1: "ETH",
	5: "ETH"
}