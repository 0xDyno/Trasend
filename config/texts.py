from config.settings import private_key_length, min_label_length, max_label_length

""" 
File With Texts
"""


"""For Main"""			#################################################
main_text_instruction = """Print number:
Show
	1 		Wallets
	1a 		Wallets + transactions
	1t		Transactions
	1at		All Txs for 1 Address
Add wallets
	2		Add
	2g 		Generate wallets
Delete wallets
	3		Delete wallets
	3a		Delete all wallets
	3t		Delete all TXs history
Send transaction (main coin)
	4		Send native (ETH)
	4a		Send native to All	(not imp)
	4e 		Send ERC-20 		(not imp)
	4ea 	Send ERC-20 to All	(not imp)
Other functions:
upd - update wallets | 01 - last block info | 02 - check connection | 03 - gas info | t - tests | e - exit"""

# Import an acc, add_wallet() method:
input_private_key = "Write your private key:"
error_not_private_key = f"\tError, it isn't private key. " \
						 f"Key should start with 0x and Length should be {str(private_key_length)}"
error_wallet_exist = "\tError, this wallet already exist in the system"
ask_label = f"Only letters and numbers, min length = {min_label_length}, max length = {max_label_length}. " \
			"Leave empty to get random.\nWrite desired label >>> "
label_wrong_length = "\tWrong length, should be from {} to {}, got {}."
label_wrong_letters = "\tOnly letters, number, spaces and underline '_', no !.,*@&#)!%"
label_exist = "\tThis label exists in the system."

# Delete an acc, remove_wallet() method:
del_instruction_to_delete_wallet = "To delete a wallet - write it's number or the address. " \
								   "To delete batch write \"last N\" or \"first N\""
del_no_wallets = "No wallets to delete"
del_successfully_deleted = "The wallet was successfully deleted"
del_out_of_index = "Wrong amount - there are no so many wallets that you want to delete"

# Text to initialize in method __new__:
new_text_load_wallets = "Loading the wallets into the system..."
new_text_load_txs = "Loading the txs into the system..."
new_text_no_wallets_to_load = "no wallets to load into the system."
new_text_no_txs_to_load = "no txs to load into the system."
new_text_no_wallets_to_init = "Init is finished."
sets_text_init_sets = "Initialize addition system files..."
upd_text_updating_wallets = "Updating the wallets info..."
upd_text_no_wallets_to_update = "No wallets to update"
upd_error_not_wallet = "Not a wallet, can't update, tell the devs >> update_wallet"

# Send TXs, TXs
tx_received = "Received"
tx_sent = "Sent"

# Other
text_no_wallets = "No wallets"
text_no_tx = "No TXs"
text_enter_wallet_or_number = "Enter wallet address or it's number:"
error_not_web3 = "Can't create Manager because got wrong Connection type. Should be {} object, got: {}"
error_add_to_set = "Error in \"add_to_set\" method, the key or label already exist in the set"
error_delete_from_set = "Error in \"delete_from_set\" method, there's no such key or label in the set"
error_wrong_generate_number = "I don't generate less, than 1 and more, than 100. Try again and choose another number"
error_no_such_address = "The address you wrote doesn't exist in the system"
error_block_doesnt_exist_yet = "The block doesn't exist in the blockchain yet"
error_no_info_about_last_block = "No info about the last block"
error_something_wrong = "Something wrong, mistake: {}\nTry again.\n\n"
success = "success"
fail = "fail"
exited = "Exited to main menu"