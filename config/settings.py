"""
File With Settings
"""
# For Manager
separator = " | "
folder = "saved/"
file_name = "saved_addresses.pickle"
saved_wallets = folder + file_name

# For Web3
gwei = "gwei"

instruction = """Print number:
1. Show all wallets
2. Add wallet
3. Delete wallet
4. Check connection
\"exit\" to finish"""

# Import an acc, add_wallet() meth:
instruction_to_add_wallet = """Write \"exit\" or leave the field empty to exit. 
Follow the instruction to add new wallet"""

input_private_key = "Please write your private key:"
private_key_length = 66
wrong_length = "Error, it isn't private key, length should be " + str(private_key_length)
wrong_first_symbols = "Error, it is not private key. Private key should start with 0x"
wrong_already_exist = "Error, this wallet already exist in the system"