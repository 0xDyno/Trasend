from config.settings import label_min_length, label_max_length

"""
Rules of texts:
1. Main menu starts with \t>>>  
2. Add \t>> (when new line) or >> (when after text) when asks user to input anything
3. Add > for program text in the beginning, no indents
4. wallet list prints with no indents
5. Initialization out of rules.
"""

"""For Main"""			#################################################
instruction_main = """\
------------------------------------------------------ Show -------------------------------------------------------
	 1 Wallets               1a Wallets + TXs             1t  Transactions          1at  All Txs for 1 Address
-------------------------------------------------- Add wallets ----------------------------------------------------
	 2 Add Wallet            2g Generate wallets	      2i Import wallets         2e Export wallets from the app
----------------------------------------------------- Delete ------------------------------------------------------
	 3 Delete wallets        3t Delete All TXs                                      4 Send ETH / ERC-20

01 	- check connection   |  02 	  - gas info    |  03 - change RPC   |
upd - update wallets     |  label - to change   |  v  - version      |  e  - exit         |  h - help (menu)\
"""
wrong_command_main = "> Wrong command. If you need instruction - print h"

# General
no_wallets = "> No wallets"
no_txs = "> No TXs"
no_txs_for_chain = "> No TXs for current chain - {}"
no_tokens = "> No Tokens"
exited = "> Exited to main menu"
success = "> Success"
fail = "> Fail"

trying_connect = "Trying to connect RPC point (node)..."

# Text to initialize in method __new__:
connected_to_rpc = "\t>>> ChainId = {}, {}"
error_chain_not_supported = "> Chain {} is not supported yet."
loading_wallets = "\tLoading the wallets into the system..."
loading_tokens = "\tLoading the tokens into the system..."
loading_txs = "\tLoading the txs into the system..."
no_wallets_to_load = no_wallets + " to load into the system."
no_tokens_to_load = no_tokens + " to load into the system."
no_txs_to_load = no_txs + " to load into the system."
init_files = "\tInitialize addition system files..."
init_finished = "Init is finished."

# Add / Generate wallet:
input_private_key = "Input private key >> "
added_wallet = "> Successfully added the wallet: {}"
error_not_private_key = f"> Error, it isn't private key 100%."
error_wallet_exist_with_label = "> Error, the key is already added to the system with the label: \"{}\""
ask_label_instruction = f"> Write desired label (only letters and numbers, no spaces, " \
						f"min length = {label_min_length}, max length = {label_max_length}) Leave empty to get random."
label_wrong_length = "> Wrong length, should be from {} to {}, got {}."
label_wrong_letters = "> Wrong label, spaces and symbols !.,*@&#)!% not allowed"
label_exist = "> This label exists in the system."
error_max_wallet_created = "> Already created max amount of wallets, {} of {}\n" + exited
error_wrong_generate_number = "> Allowed to create {} more wallets in total (exists {} of {} max). " \
							  "I can generate from 1 to {}, you asked: {}"
get_path = "Full path to the file >> "

# Sets add - delete
error_add_to_set = "> Error in \"add_to_set\" method, {addr-label-key} already exist in the set"
error_delete_from_set = "> Error in \"delete_from_set\" method, there's no {addr-label-key} in the set"

# Deleting accs:
instruction_to_delete_wallet = "> Write wallets to delete (address or label or number, separate with spaces). " \
								   "Use \"last N\", \"first N\" or \"all\" to delete batch"
deleted_successfully = "> The wallet was successfully deleted"
del_out_of_index = "> Wrong amount - there are no so many wallets that you want to delete"

# Send function
what_to_send = "Press Enter to send {} or drop me contract address (token) >> "
error_not_contract_address = "> That's not contract address 100%, check it one more time and try again."
choose_receivers = """> Choose receivers, they should be separated by spaces (1 2 any_label 6 21991656 0x690b9... etc)
\t\t\t'all' - send to all | 'file' - load from file"""
tx_received = "Received"
tx_sent = "Sent"

# Other
# input_wallet_identifier = "To choose wallet enter its address, label or number:"
error_not_web3 = "> Can't create Manager because got wrong Connection type. Should be {} object, got: {}"
error_no_such_address = "> The address you wrote doesn't exist in the system"
change_label = "> Successfully changed old \"{}\" to new \"{}\" for {}"