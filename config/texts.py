from config.settings import private_key_length, label_min_length, label_max_length

"""For Main"""			#################################################
instruction_main = """Print number:
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
wrong_command_main = "Wrong command. If you need instruction - print h"

# General
no_wallets = "No wallets"
no_txs = "No TXs"
no_tokens = "No Tokens"
exited = "\tExited to main menu"
success = "Success"
fail = "Fail"

trying_connect = "Trying to connect RPC point (node)..."

# Text to initialize in method __new__:
connected_to_rpc = "\t>>> ChainId = {}, {}"
error_chain_not_supported = "Chain {} is not supported yet."
loading_wallets = "\tLoading the wallets into the system..."
loading_tokens = "\tLoading the tokens into the system..."
loading_txs = "\tLoading the txs into the system..."
no_wallets_to_load = no_wallets + " to load into the system."
no_tokens_to_load = no_tokens + " to load into the system."
no_txs_to_load = no_txs + " to load into the system."
init_files = "\tInitialize addition system files..."
init_finished = "Init is finished."

# Add / Generate wallet:
input_private_key = "Write your private key:"
added_wallet = "Successfully added the wallet: {}"
error_not_private_key = f"\tError, it isn't private key. " \
						 f"Key should start with 0x and Length should be {str(private_key_length)}"
error_wallet_exist_with_label = "Error, the key is already added to the system with the label: \"{}\""
ask_label = f"Only letters and numbers, min length = {label_min_length}, max length = {label_max_length}. " \
			"Leave empty to get random.\nWrite desired label >>> "
label_wrong_length = "\tWrong length, should be from {} to {}, got {}."
label_wrong_letters = "\tOnly letters, number, spaces and underline '_', no !.,*@&#)!%"
label_exist = "\tThis label exists in the system."
error_max_wallet_created = "Already created max amount of wallets, {} of {}\n" + exited
error_wrong_generate_number = "Allowed to create {} more wallets in total (exists {} of {} max). " \
							  "I can generate from 1 to {}, you asked: {}"

# Sets add - delete
error_add_to_set = "Error in \"add_to_set\" method, {addr-label-key} already exist in the set"
error_delete_from_set = "Error in \"delete_from_set\" method, there's no {addr-label-key} in the set"

# Deleting accs:
instruction_to_delete_wallet = "To delete a wallet - write it's number or the address. " \
								   "To delete batch write \"last N\" or \"first N\""
deleted_successfully = "The wallet was successfully deleted"
del_out_of_index = "Wrong amount - there are no so many wallets that you want to delete"

# Send function
what_to_send = "Press enter to send {} or drop me contract address (token) >> "
error_not_contract_address = "That's not contract address 100%, check it one more time and try again."
choose_receivers = """
You can: 
1. choose 1 receiver or more, they should be separated by spaces
2. Write 'all' to send to all in the system or 'list' (not realized yet) to drop the list of senders. 
Example choose batch >>> 1 2 any_label 6 21991656 27 13 83 127 0x690b9a9e9aa1c9db991c7721a92d351db4fac990 92 39 12"""
tx_received = "Received"
tx_sent = "Sent"

# Other
# input_wallet_identifier = "To choose wallet enter its address, label or number:"
error_not_web3 = "Can't create Manager because got wrong Connection type. Should be {} object, got: {}"
error_no_such_address = "The address you wrote doesn't exist in the system"
error_block_doesnt_exist_yet = "The block doesn't exist in the blockchain yet"
error_no_info_about_last_block = "No info about the last block"
error_something_wrong = "Something wrong, mistake: {}\nTry again.\n\n"
error_cant_update = "Not a wallet, can't update, tell the devs >> update_wallet"