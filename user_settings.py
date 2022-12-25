from config.rpcs import *
"""
Warning! I suggest avoid using Default RPCs, they aren't stable

Default RPCs Mainnet:
    MAINNET_ETH
    MAINNET_BNB
    MAINNET_ARBITRUM
    MAINNET_MATIC
    MAINNET_AVALANCHE
    MAINNET_FANTOM
    MAINNET_MOONBEAM
Default RPCs Testnet:
    TESTNET_ETH_GOERLI
    TESTNET_BNB
    TESTNET_ARBITRUM_GOERLI
    TESTNET_AVALANCHE_FUJI
    TESTNET_FANTOM
    
# RPC point is used for interaction with blockchain. You can use your own or setup default RPC:
# PRC_point = "https://eth-mainnet.g.alchemy.com/v2/your_code_92KIEWfh8wefj9-Wdiqwed3"
# RPC_point = "your_rpc_point_http"
"""
RPC_Point = TESTNET_ETH_GOERLI
max_connections = 20      # max connections per moment

# Gas settings:
update_gas = 5            # updates gas every N seconds, min = 1

multiply_gas = 1.3        # Multiply GAS       (will Not be used more, then required)
multiply_gas_price = 1.1  # Multiply gas price (will Not be used more, then required, BNB & Fantom will use 100%)
multiply_priority = 1.1   # Multiply priority  (will be used 100% if a chain supports all updates
#                                               if the chain doesn't support last update - won't be used at all)

min_gas_price = 0         # (gwei) Minimal Gas Price per 1 GAS
min_priority = 0          # (gwei) Minimal Priority
# If gas price after multiplying less, than min - it will use min. In GWEI