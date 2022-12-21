import binascii
import os
import pickle
import time
from random import random
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from eth_typing import ChecksumAddress
from web3 import Web3
from eth_account import Account
from cryptography.fernet import Fernet

from config import settings, texts
from src import threads, trans, manager
from src.classes import Wallet, Token

"""
File with general methods to alleviate Manager (make it easy to read)
Not important methods/functions which doesn't work with data directly will be here
"""


def confirm(print_before=None):
    if print_before is not None:
        print(print_before)
    return input("> Are you sure? Write \"y\" to confirm: ").lower().strip() == "y"


def is_it_addr(line: str) -> bool:
    """return True if it's like address. False - if it's 100% not address"""
    return line.startswith("0x") and len(line) == settings.address_length


def is_it_key(line: str) -> bool:
    """return True if it's like private key. False - if it's 100% not private key"""
    return line.startswith("0x") and len(line) == settings.private_key_length


def get_new_connection() -> Web3:
    connection = print_ask(text_in_input="Write new connection > ")
    print(texts.trying_connect, end=" ")
    
    connection = Web3(Web3.HTTPProvider(connection))
    if connection.isConnected():
        print(texts.success)
        return connection
    else:
        print(texts.fail)
        raise ValueError(texts.exited)
        

def get_fernet_key():
    with open(settings.crypto_key, "rb") as r:
        return r.read()


def print_ask(wallets=None, text_before=None, text_after=None, text_in_input=None) -> str:
    """Prints wallets and text if given, ask to input text.
    -> Use this when you don't need to print wallets.
    -> If you need print wallets - use inner method of Manager
    :param wallets: list with wallets
    :param text_before: prints text before wallets list
    :param text_after: prints text after wallets list
    :param text_in_input: print text and ask to input in the same line
    :return: user's input if it's not empty"""
    if text_before is not None:
        print(text_before)			    # print text_before is there's
        
    if wallets is not None:
        print_wallets(wallets)  		# prints wallets is not None
        
    if text_after is not None:
        print(text_after)			    # print text_after is there's
        
    if text_in_input is not None:	    # Choose how to ask - in the same line
        users_input = input("\t" + text_in_input).strip().lower()
    else:							    # or on the next line
        users_input = input().strip().lower()
        
    if not users_input:                 # check it's not empty
        raise InterruptedError(texts.exited)
    return users_input					# return


def print_wallets(list_with_wallets):
    """Prints wallets with its index"""
    length = len(list_with_wallets)
    for i in range(length):  			# print all addresses
        print("{:>3}. {}".format(i + 1, list_with_wallets[i]))


def print_all_info(list_with_wallets):
    """Prints wallets with its index and TXs list"""
    length = len(list_with_wallets)									# prints info with TXs
    for i in range(length):											# and its index
        print("{:>3}. {}".format(i + 1, list_with_wallets[i].get_all_info()))


def print_all_txs(chain_id: int):
    """Prints all TXs with current network (chainId)"""
    all_txs_for_chain = [tx for tx in manager.Manager.all_txs if chain_id == tx.chain_id]       # get all txs for chain
    if not all_txs_for_chain:                                                                    # if no TXs - tell it
        raise ValueError(texts.no_txs_for_chain.format(settings.chain_name[chain_id]))
    [print(tx) for tx in all_txs_for_chain]                                                     # or print them


def print_txs_for_wallet(chain_id: int, wallet: Wallet):
    """Prints wallet all txs for the wallet in given network"""
    print(settings.chain_name[chain_id] + " | " + wallet.__str__())
    update_txs_for_wallet(wallet)

    for tx in wallet.txs:
        if tx.chain_id == chain_id:
            print("\t" + tx.str_no_bc())


def generate_label(set_with_labels):
    """Generates unique label from numbers in defined length from settings"""
    while True:
        number = int(random() * 10 ** settings.label_gen_length)	# it works..
        if number >= 10 ** (settings.label_gen_length - 1):
            label = str(number)
            try:
                check_label(set_with_labels, label)
                return label
            except ValueError as e:
                raise ValueError(" >Wrong settings, can't generate the label:", e)


def ask_label(set_with_labels: set, instruction: str = None):
    if instruction is None:
        instruction = texts.ask_label_instruction
    print(instruction)
    while True:
        label = input("\t>> ").strip()
        if not label:									# If empty - generate number
            return generate_label(set_with_labels)
        try:
            check_label(set_with_labels, label)			# Check if it's Ok.
            return label									# and return
        except ValueError as e:			# If not
            print(e)					# Tell the mistake


def check_label(label_set: set, label):
    if label.lower() == "exit" or label.lower() == "e":     # Check exit
        raise InterruptedError(texts.exited)

    if len(label) > settings.label_max_length or len(label) < settings.label_min_length:  	    # Check length
        raise ValueError(texts.label_wrong_length.format(settings.label_min_length,
                                                         settings.label_max_length, len(label)))
    if not label.isalnum():
        raise ValueError(texts.label_wrong_letters)

    if label_set:				# Then check if the label exist
        if label in label_set:
            raise ValueError(texts.label_exist)


def check_private_key(keys: set, wallets: list, key: str):
    if not key:
        raise InterruptedError(texts.exited)

    if not is_it_key(key):
        raise ValueError(texts.error_not_private_key)

    if keys:									# if keys not empty...
        if key in keys:  						# If exits - tell the label of the wallet
            label = "> Mistake, can't find"
            for wallet in wallets:  			# find this wallet
                if key == wallet.key():  		# if this wallet - same what the user wrote
                    label = wallet.label  		# get the label
            raise ValueError(texts.error_wallet_exist_with_label.format(label))

    try:									# last check - to be sure that's
        Account.privateKeyToAccount(key).address	# 100% private key
    except binascii.Error:
        raise ValueError(texts.error_not_private_key)
    

def check_wallets(wallets: list) -> True:
    if not wallets:
        raise ValueError(texts.no_wallets)
    return True
    
    
def check_wallet_type(wallet: Wallet) -> bool:
    if not isinstance(wallet, Wallet):
        raise ValueError("Wallet obj is required and that's not a Wallet")
    return True


def generate_wallets(w3, set_labels, set_keys, number) -> list:
    """Generates wallets and returns list with updates wallets
    :return: list with updated Wallets
    """
    new_generated_wallets = list()
    list_daemons = list()
    print(f"> Started the generation {number} wallets")
    for _ in range(number):
        while not threads.can_create_daemon():		# If we can't create daemon - sleep
            if number > 50:							# or draw progress bar
                create_progress_bar(len(new_generated_wallets), number)
            time.sleep(settings.wait_to_create_daemon_again)

        daemon = threads.start_todo(generate_wallet, False, w3, set_labels, set_keys, new_generated_wallets)
        list_daemons.append(daemon)										# add to the list
    [daemon.join() for daemon in list_daemons if daemon.is_alive()]		# wait till they finish
    return new_generated_wallets										# return the list


def generate_wallet(w3, set_labels, set_keys, result_list):
    """Generates unique 1 wallet (key + label). Updates it and add to the list
    """
    key = w3.toHex(w3.eth.account.create().key) 	# get private key
    if key not in set_keys:  						# check we don't have it
        label = generate_label(set_labels)  		# generate unique label
        wallet = Wallet(key, label)  				# create wallet
        update_wallet(w3, wallet, set_labels)		# update it

        result_list.append(wallet)				# save it
    else:										# If we have that key - try again... tho I doubt it
        generate_wallet(w3, set_labels, set_keys, result_list)	# just in case...


def update_wallets(w3: Web3, wallets, set_labels):
    """Create threads to update wallets and sync TXs"""
    check_wallets(wallets)

    list_daemons = list()
    for wallet in wallets:  # for each wallet
        if threads.can_create_daemon():  # if allowed thread creating - start a new thread
            thread = threads.start_todo(update_wallet, True, w3, wallet, set_labels, True)
            list_daemons.append(thread)  # add thread to the list
        else:
            time.sleep(settings.wait_to_create_daemon_again)

    [daemon.join() for daemon in list_daemons if daemon.is_alive()]  # wait will all threads finish


def update_wallet(w3: Web3, wallet: Wallet, set_labels: set, update_tx=False):
    """
    Receives Wallet. If the wallet doesn't have an address - method parses it and adds
    After that it updates balance, nonce & sync TXs if asked
    """
    check_wallet_type(wallet)
    if not wallet.addr or not wallet.addr_lower:  					# if the wallet doesn't have address
        key = wallet.key()  										# get private key
        wallet.addr = Account.privateKeyToAccount(key).address  	# parse the address and add
        wallet.addr_lower = wallet.addr.lower()

    if wallet.label is None:
        wallet.label = generate_label(set_labels)

    wallet.balance_in_wei = w3.eth.get_balance(wallet.addr)  		# update balance
    wallet.nonce = w3.eth.get_transaction_count(wallet.addr)  		# update nonce

    if update_tx:
        update_txs_for_wallet(wallet)  # updates txs list and each tx if status == None
        [trans.update_tx(w3, tx) for tx in wallet.txs if tx.status is None]


def get_wallet_index(wallets_list: list, set_addr: set, set_labels: set, line: str | Wallet) -> int:
    """
    Returns wallet index in the list from: Waller obj or it's number, label or address.
    :param wallets_list: list with wallets
    :param set_addr: set with addresses
    :param set_labels: set with labels
    :param line: address or label or number (starts from 1)
    :return: Index of selected Wallet in the list
    """
    if isinstance(line, Wallet):
        for i in range(len(wallets_list)):
            if wallets_list[i].key() == line.key():
                return i

    if line.isnumeric() and len(line) < 4:		# Min length for label = 4 chars.
        number = int(line)						# If it's less -> that's number
        if number < 1 or number > len(wallets_list):
            raise ValueError("Wrong number" + "\n" + texts.exited)
        return number - 1
    # Tho... that should be addr or label, let's check it
    if line not in set_addr and line not in set_labels:
        raise ValueError(texts.error_no_such_address + "\n" + texts.exited)

    line = line.lower()
    for i in range(len(wallets_list)):
        if wallets_list[i].addr_lower == line or wallets_list[i].label == line:
            return i


def import_addrs(path: str):
    """Load addresses from a file, 1 addr per line"""
    with open(path, "r") as reader:
        addr_list = reader.read().strip().split("\n")

    receivers = list()
    for addr in addr_list:
        if addr:
            try:
                receivers.append(Web3.toChecksumAddress(addr))
            except (TypeError, ValueError):
                print(f"> {addr} is not address")

    return receivers


def delete_txs_history(wallets: list):
    if manager.Manager.all_txs:
        [wallet.txs.clear() for wallet in wallets]		# delete TXs from wallets
        manager.Manager.all_txs.clear()					# clear the set


def update_txs_for_wallet(wallet):
    if wallet.txs:							# skip 1 check on each iteration if there are no txs at all
        for tx in manager.Manager.all_txs:
            if (wallet.addr == tx.receiver or wallet.addr == tx.sender) and tx not in wallet.txs:
                wallet.txs.append(tx)
    else:
        for tx in manager.Manager.all_txs:
            if wallet.addr == tx.receiver or wallet.addr == tx.sender:
                wallet.txs.append(tx)


def is_contract_exist(chain_id: int, sc_addr: str) -> bool:
    """
    Checks do we have that contract address in the system or not
    :param chain_id: chain ID
    :param sc_addr: address of smart contract
    :return: True if we have that contract, Flase if we don't have
    """
    set_tokens = manager.Manager.all_tokens.get(f"addresses_{chain_id}")
    if not set_tokens or sc_addr.lower() not in set_tokens:
        return False
    return True


def get_token(w3: Web3, smart_contract_addr: ChecksumAddress) -> Token:
    """
    If the tokens exists in the system - returns it
    Else - creates & returns
    :return: Token
    """
    chain_id = w3.eth.chain_id
    
    if not is_contract_exist(chain_id, smart_contract_addr):
        return trans.update_erc_20(w3, smart_contract_addr)
    
    for token in manager.Manager.all_tokens[f"tokens_{chain_id}"]:
        if token.chain_id == chain_id and token.sc_addr == smart_contract_addr:
            return token


def add_smart_contract_token(chain_id: int, sc_addr: str, symbol: str,
                             decimal: int, abi) -> Token:
    """Creates token and add it to the sets. If new chain and there
        no sets created -> first creates the sets and then adds
    :return: created token"""
    new_token = Token(chain_id, sc_addr, symbol, decimal, abi)
    
    # If it's a new chain and sets aren't created - create them
    tokens = f"tokens_{chain_id}"
    addr = f"addresses_{chain_id}"

    if tokens not in manager.Manager.all_tokens:
        manager.Manager.all_tokens[tokens] = set()

    if addr not in manager.Manager.all_tokens:
        manager.Manager.all_tokens[addr] = set()
    
    # Add the token and it's address
    sc_addr = sc_addr.lower()
    manager.Manager.all_tokens.get(f"tokens_{chain_id}").add(new_token)
    manager.Manager.all_tokens.get(f"addresses_{chain_id}").add(sc_addr)
    
    return new_token


def export_wallets(wallets: list):
    time_ = str(datetime.strftime(datetime.fromtimestamp(time.time()), "%Y_%H%M%S"))
    path = os.path.join(os.getcwd() + "/" + settings.folder + "wallet_export_" + time_ + ".txt")
    with open(path, "w") as w:
        for wallet in wallets:
            w.write(f"{wallet.key()} {wallet.label} {wallet.addr}\n")
    print("> Wallets were exported in format \"key label addr\" to >", path)


def import_wallets(file_path: str, wallets: list, keys: set, labels: set) -> list:
    """
    Imports wallets from file. Required format (key label addr), 1 per line. Doesn't update
    :param file_path: full path to the file
    :param wallets:	list with all wallets from Manager
    :param keys: set with all keys from Manager
    :param labels: set with all labels from Manager
    :return: list with imported wallets
    """
    unique_data = set()

    def check_duplicates():					# check there's no duplicates
        for i in range(len(elements)):
            if elements[i] in unique_data:
                unique_data.add(elements[i])
                return elements[i]
            unique_data.add(elements[i])
        return False

    wallets_list = list()
    with open(file_path) as r:				# get info form file
        lines = r.read().split("\n")		# divide to lines

    for line in lines:						# for each lne
        if not line:						# that isn't empty
            continue
        elements = line.split()				# divide by space

        if check_duplicates():				# check duplicates
            print("> Found Duplicated Info, That can Crash the System > ", end="")
            [print(x, end=" ") for x in elements]
            print()
            continue

        key = elements[0]					# get key and check it - if not Ok - we pass it
        try:
            check_private_key(keys, wallets, key)
            try:							# If Ok - get the label
                label = elements[1]
                check_label(labels, label)
            except IndexError:
                label = generate_label(labels)  	    # if label not Ok - generate label
                print("> Wasn't able to import label for the key {} | Generated > {}".format(key, label))
            except (InterruptedError, ValueError) as e:
                label = generate_label(labels)		    # if label not Ok - generate label
                print("> Wasn't able to import label for the key {} | Generated > {} | error: {}".format(key, label, e))
        except (InterruptedError, ValueError) as e:
            print("> Wasn't able to import wallet with the key: {} {}".format(key, e))
        else:
            wallets_list.append(Wallet(key, label))		# and finally - add the wallet to the list
    return wallets_list


def check_balances(balance, wish_send, receivers=1):
    if not wish_send:
        raise InterruptedError("> Not a number. Exited.")
    try:
        balance = Decimal(balance)
        wish_send = Decimal(wish_send)
    except InvalidOperation:
        raise InterruptedError("> Not a number. Exited.")
    required = wish_send * receivers
    if required > balance:
        raise InterruptedError("> Not enough funds. Required {:.2f}, you have {:.2f}".format(required, balance))


def check_saveloads_files(folder: str, path_to_file: str) -> bytes:
    """
    Checks if the directory and files exist. 5 conditions:
    1. File and Key exists - return key (everything Okay)
    
    In all next cases we have to create file. And get OR create Key.
    So Key is written in the condition, file creation - in the end
    
    2. no Folder                     -->> create Folder, Key
    3. no File     - no Key          -->> create Key
    4. no File     - Key exists      -->> get Key
    5. File exists - no Key          -->> rename old file, get Key
                                        + for all of them: creat File
    :param folder: 			str -> "folder/"
    :param path_to_file: 	str -> "folder/name_of_your_file"
    :return: cryptography key
    """
    def create_cryptography_key():
        new_key = Fernet.generate_key()
        with open(settings.crypto_key, "wb") as w:
            w.write(new_key)
        return new_key

    # 2. If no folder              -->> Create Folder & Key
    if not os.path.isdir(folder):
        os.mkdir(folder)
        key = create_cryptography_key()

    # 1. If File and Key exists    -->> get Key & return
    elif os.path.exists(path_to_file) \
            and os.path.exists(settings.crypto_key):
        return get_fernet_key()

    # 3. No File - no Key		    -->> create Key
    elif not os.path.exists(path_to_file) \
            and not os.path.exists(settings.crypto_key):
        key = create_cryptography_key()

    # 4. No File - yes Key		    -->> get Key
    elif not os.path.exists(path_to_file) \
            and os.path.exists(settings.crypto_key):
        key = get_fernet_key()

    # 5. Yes File - no Key		    -->> rename old_file & create Key
    else:
        creation_date_in_ns = os.stat(path_to_file).st_birthtime			# get the date of creation
        creation_date = str(date.fromtimestamp(creation_date_in_ns))		# transform into YYYY-MM-DD
        os.rename(path_to_file, f"{path_to_file}_old_{creation_date}")  	# rename
        key = create_cryptography_key()

    open(path_to_file, "w").close()     # create file for conditions: 2 3 4 5
    return key


def save_data(data, folder, filepath):
    """
    Received folder name and file name. Saves encoded data to folder/name_file
    :param data: 		data to save (if empty - will clear the file)
    :param folder: 		str -> "folder/"
    :param filepath: 	str -> "folder/name_of_your_file"
    :return: loaded obj or None
    """
    if not data:						# if empty
        open(filepath, "w").close()		# clear the file
    else:
        key = check_saveloads_files(folder, filepath)		# check data and get secret
        fernet = Fernet(key)								# get key from secret

        data_to_save = fernet.encrypt(pickle.dumps(data))	# dumps -> encode
        with open(filepath, "wb") as w:						# write
            w.write(data_to_save)


def load_data(folder, filepath):
    key = check_saveloads_files(folder, filepath)		# check data and get secret
    fernet = Fernet(key)								# get key from secret

    with open(filepath, "rb") as r:
        encrypted_bytes = r.read()

    if encrypted_bytes:
        bytes_ = fernet.decrypt(encrypted_bytes)
        return pickle.loads(bytes_)
    else:
        return None


def create_progress_bar(current, finish):
    """Just "progress bar" """
    step = 1.005
    while finish > 80:				# equalize to 100 max
        finish = finish / step
        current = current / step
    while finish < 80:
        finish = finish * step
        current = current * step
    current = int(current)
    finish = 80 - current

    print("." * current, end="")
    print(" " * finish, end="")
    current = int(current * 1.26)
    if current < 10:
        print(f" | ( {current}% / 100%)")
    else:
        print(f" | ({current}% / 100%)")
