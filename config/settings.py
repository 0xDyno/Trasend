"""
File With Settings
"""
# Static
private_key_length = 66
address_length = 42

""" For Manager """		#################################################
separator = " | "
folder = "saved/"
file_name = "saved_addresses.pickle"
saved_wallets = folder + file_name

# Import an acc, add_wallet() method:
add_input_private_key = "Please write your private key:"
add_error_wrong_length = "Error, it isn't private key, length should be " + str(private_key_length)
add_error_wrong_first_symbols = "Error, it is not private key. Private key should start with 0x"
add_error_wrong_already_exist = "Error, this wallet already exist in the system"

# Delete an acc, remove_wallet() method:
del_instruction_to_delete_wallet = "Write the address you want to delete or it's number:"
del_error_not_number_or_address = "That's not wallet address or number"
del_wrong_number = "Wrong number, there's no wallet under this number"
del_successfully_deleted = "The wallet was successfully deleted"
del_error_no_such_address = "The address you wrote doesn't exist in the system"
del_no_wallets = "No wallets to delete"

# Text to initialize in method __new__:
new_text_load_the_wallets = "Working: loading the wallets into system..."
new_text_no_wallets_to_init = "No wallets added, init is finished."
upd_text_updating_wallets = "Working: updating the wallets info..."
upd_text_no_wallets_to_update = "No wallets to update"
sets_text_init_sets = "Initialize addition system files..."

# Other
text_no_wallets_to_print = "No wallets to show"
error_add_to_set = "Error in \"add_to_set\" method, the key or label already exist in the set"
error_delete_from_set = "Error in \"delete_from_set\" method, there's no such key or label in the set"


""" For Web3"""			#################################################
gwei = "gwei"

"""For Main"""			#################################################
main_text_instruction = \
"""Print number:
1. Show all wallets
2. Add wallet
3. Delete wallet
4. Check connection
5. Update wallets
\"exit\" to finish"""