"""
File With Settings
"""
# Static
private_key_length = 66
address_length = 42

"""For Main"""			#################################################
main_text_instruction = \
"""Print number:
1. Show all wallets
2. Add wallets
3. Generate wallets
4. Delete wallets
5. Check connection
6. Update wallets
\"exit\" to finish"""

""" For Manager """		#################################################
separator = " | "
folder = "saved/"
file_name = "saved_addresses.pickle"
saved_wallets = folder + file_name

# Import an acc, add_wallet() method:
add_input_private_key = "Write your private key:"
add_error_wrong_length = "Error, it isn't private key, length should be " + str(private_key_length)
add_error_wrong_first_symbols = "Error, it is not private key. Private key should start with 0x"
add_error_wrong_already_exist = "Error, this wallet already exist in the system"
add_ask_label = "Write desired label (or empty to get random) >>> "

# Delete an acc, remove_wallet() method:
del_instruction_to_delete_wallet = """3 ways to deletes accs:
1. Write the address
2. Write the number
3. Write "last N" to delete batch of last accs. Example - last 10
List of existed wallets:"""
del_wrong_number = "Wrong number"
del_successfully_deleted = "The wallet was successfully deleted"
del_error_no_such_address = "The address you wrote doesn't exist in the system"
del_no_wallets = "No wallets to delete"

# Text to initialize in method __new__:
new_text_load_the_wallets = "Working: loading the wallets into system..."
new_text_no_wallets_to_init = "No wallets to add, init is finished."
sets_text_init_sets = "Initialize addition system files..."
upd_text_updating_wallets = "Working: updating the wallets info..."
upd_text_no_wallets_to_update = "No wallets to update"
upd_error_not_wallet = "Not a wallet, can't update, tell the devs >> update_wallet"

# Other
text_no_wallets_to_print = "No wallets to show"
error_add_to_set = "Error in \"add_to_set\" method, the key or label already exist in the set"
error_delete_from_set = "Error in \"delete_from_set\" method, there's no such key or label in the set"
error_more_than_100 = "I don't generate more wallets, than 100. Choose another number"