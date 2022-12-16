"""Static""" 			#################################################
private_key_length = 66
address_length = 42
gas_for_native = 21000
supported_chains = {1, 5, 56}

""" For Manager """		#################################################
folder = "private/"
saved_wallets = folder + "saved_wallets"
saved_tokens = folder + "saved_tokens"
saved_txs = folder + "saved_txs"
crypto_key = folder + "key"
max_generate_addr = 999
# I didn't put max_accounts check to inner _add_wallet, to let load saved wallets (if different settings was before)
max_wallets = 999			# Attention!! Shouldn't be more, or increase min_label_length
label_min_length = 4		# Attention!! The program works property ONLY if length is less, than 4 !!
label_max_length = 20		# Shouldn't be more, than 42
label_gen_length = 8

"""Daemons"""			#################################################
print_daemons_info = False			# prints info from daemons
update_block_every = 3				# 12 secs for ETH
update_gas_every = 5				#
max_threads_per_time = 20			# not more than N threads
wait_to_create_daemon_again = 1		# If no free place to create a daemon - it will wait that time before try again

"""Transactions"""		#################################################
print_trans_info = False		# prints info when does a transaction
multiply_gas = 1.1				# Multiply counted gas (won't be used more, then required)
multiply_gas_price = 1.2		# to multiply gas price (won't be used more, then required)
multiply_priority = 1.5			# to multiply priority (will be paid full price 100%)

# If current GasPrice * MultiplyGasPrice < than minimum - then will be used min
min_gas_price = 3				# in gwei
min_priority = 0.5				# in gwei
gas_native = 21000
# gas and average gas for erc20 - just in case estimating didn't work.
gas_erc20 = 100000				# max gas to send ETC20 token
average_gas_erc20 = 60000		# average gas required to send TX

tx_slash = "tx/"
chain_explorers = {
	1: "https://etherscan.io/",
	5: "https://goerli.etherscan.io/",
	56: "https://bscscan.com/"
}
chain_default_coin = {
	1: "ETH",
	5: "ETH",
	56: "BNB"
}
chain_name = {
	1: "ETH mainnet",
	5: "Goerli ETH testnet",
	56: "BNB mainnet"
}
ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'