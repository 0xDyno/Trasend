import user_settings

""" For Manager """		################################################################################################
version = "0.1.3"
folder = "private/"
saved_wallets = folder + "saved_wallets"
saved_tokens = folder + "saved_tokens"
saved_txs = folder + "saved_txs"
crypto_key = folder + "key"
max_generate_addr = 100
# I didn't put max_accounts check to inner _add_wallet, to let load saved wallets (if different settings was before)
max_wallets = 999			# Attention!! Shouldn't be more, or increase min_label_length
label_min_length = 4		# Attention!! The program works property ONLY if length is less, than 4 !!
label_max_length = 20		# Shouldn't be more, than 42
label_gen_length = 8

"""Daemons"""			################################################################################################
print_daemons_info = False			# prints info from daemons
update_gas_every = user_settings.update_gas
max_threads_per_time = user_settings.max_connections
wait_to_create_daemon_again = 1		# If max threads created - it will wait N sec before try again

"""Transactions"""		################################################################################################
print_trans_info = False		# prints info when does a transaction
multiply_gas = user_settings.multiply_gas
multiply_gas_price = user_settings.multiply_gas_price
multiply_priority = user_settings.multiply_priority

# If current GasPrice * MultiplyGasPrice < than minimum - then will be used min
min_gas_price = user_settings.min_gas_price
min_priority = user_settings.min_priority
gas_native = 21000
# gas and average gas for erc20 - just in case estimating didn't work.
gas_erc20 = 100000				# max gas to send ETC20 token
average_gas_erc20 = 60000		# average gas required to send TX

chain_explorers = {
    1: "https://etherscan.io/",
    56: "https://bscscan.com/",
    42161: "https://arbiscan.io/",
    137: "https://polygonscan.com/",
    43114: "https://snowtrace.io/",
    250: "https://ftmscan.com/",
    1284: "https://moonbeam.moonscan.io/",
    5: "https://goerli.etherscan.io/",
    97: "https://testnet.bscscan.com/",
    421613: "https://testnet.arbiscan.io/",
    43113: "https://testnet.snowtrace.io/",
    4002: "https://testnet.ftmscan.com/",
}
chain_default_coin = {
    1: "ETH",
    56: "BNB",
    42161: "ETH",
    137: "MATIC",
    43114: "AVAX",
    250: "FTM",
    1284: "GLMR",
    5: "ETH",
    97: "tBNB",
    421613: "ETH-AGOR",
    43113: "AVAX",
    4002: "FTM",
}
chain_name = {
    1: "Mainnet ETH",
    56: "Mainnet BNB",
    42161: "Mainnet Arbitrum",
    137: "Mainnet MATIC",
    43114: "Mainnet Avalanche",
    250: "Mainnet Fantom",
    1284: "Mainnet Moonbeam",
    5: "Testnet ETH Goerli",
    97: "Testnet BNB",
    421613: "Testnet Arbitrum Goerli",
    43113: "Testnet Avalanche Fuji",
    4002: "Testnet Fantom",
}
# 1 - usual TXs
# 2 - london update, uses only used gas_price
# 3 - more updates, burn & adds priority
chain_update_type = {
    1: 3,       # Mainnet ETH
    56: 1,      # Mainnet BNB
    42161: 2,   # Mainnet Arbitrum
    137: 3,     # Mainnet MATIC
    43114: 3,   # Mainnet Avalanche
    250: 1,     # Mainnet Fantom
    1284: 3,    # Mainnet Moonbeam
    5: 3,       # Testnet ETH Goerli
    97: 1,      # Testnet BNB
    421613: 2,  # Testnet Arbitrum Goerli
    43113: 3,   # Testnet Avalanche Fuji
    4002: 1,    # Testnet Fantom
}

ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,' \
      '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},' \
      '{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,' \
      '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply",' \
      '"outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},' \
      '{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad",' \
      '"type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,' \
      '"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad",' \
      '"type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable",' \
      '"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],' \
      '"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"",' \
      '"type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,' \
      '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{' \
      '"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,' \
      '"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{' \
      '"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,' \
      '"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},' \
      '{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance",' \
      '"outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},' \
      '{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,' \
      '"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad",' \
      '"type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,' \
      '"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad",' \
      '"type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,' \
      '"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit",' \
      '"type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,' \
      '"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}] '