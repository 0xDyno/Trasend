from config.settings import private_key_length

""" 
File With Texts
"""


"""For Main"""			#################################################
main_text_instruction = """Print number:
1. Show all wallets
2. Add wallets
3. Generate wallets
4. Delete wallets
5. Check connection
6. Update wallets
7. Last Block Info
8. ---- Send transaction (not implemented)
9. ----
-------
t - for tests
\"exit\" or \"e\" to finish"""

# Import an acc, add_wallet() method:
add_input_private_key = "Write your private key:"
add_error_wrong_format = f"Error, it isn't private key. " \
						 f"Key should start with 0x and Length should be {str(private_key_length)}"
add_error_wrong_already_exist = "Error, this wallet already exist in the system"
add_ask_label = "Write desired label (or Enter to get random) >>> "

# Delete an acc, remove_wallet() method:
del_instruction_to_delete_wallet = """3 ways to delete wallets:
1. Write the address
2. Write the number
3. Write "last N" to delete batch of last wallets. Example - "last 10"
4. Write "all" to delete all wallets
List of existed wallets:"""
del_no_wallets = "No wallets to delete"
del_successfully_deleted = "The wallet was successfully deleted"

# Text to initialize in method __new__:
new_text_load_the_wallets = "Working: loading the wallets into the system..."
new_text_not_wallets_to_load = "no wallets to load into the system."
new_text_no_wallets_to_init = "Init is finished."
sets_text_init_sets = "Initialize addition system files..."
upd_text_updating_wallets = "Working: updating the wallets info..."
upd_text_no_wallets_to_update = "No wallets to update"
upd_error_not_wallet = "Not a wallet, can't update, tell the devs >> update_wallet"

# Other
text_no_wallets = "No wallets"
text_enter_wallet_or_number = "Enter wallet address or it's number:"
error_add_to_set = "Error in \"add_to_set\" method, the key or label already exist in the set"
error_delete_from_set = "Error in \"delete_from_set\" method, there's no such key or label in the set"
error_wrong_generate_number = "I don't generate less, than 1 and more, than 100. Try again and choose another number"
error_no_such_address = "The address you wrote doesn't exist in the system"
error_not_number_or_address = "Error, not number or address"
error_block_doesnt_exist_yet = "The block doesn't exist in the blockchain yet"
error_no_info_about_last_block = "No info about the last block"
success = "success"
fail = "fail"