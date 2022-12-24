import time

from web3 import Web3

from config import texts, settings
from src import assist, trans, threads, logs
from src.classes import Wallet


class Manager:
    """
    To manage wallets and all operations. Realisation for:
    > operations that don't change data directly - located in assist.py
    > operations that related to transaction     - located in trans.py
    
    all_tokes -> dict
        for each chain:
            - tokens_chainID    -> set with tokens
            - addresses_chainID -> set with addresses (lower case)
    """
    __singleton = None
    all_txs = list()
    all_tokens = dict()
    
    network_gas_price = None
    network_max_priority = None
    gas_price = None
    max_priority = None

########################################################################################################################
# Initialization #######################################################################################################
########################################################################################################################

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = super().__new__(cls)
            cls.__singleton.__is_initialized = False

        return cls.__singleton

    def __del__(self):
        Manager.__singleton = None

    def __init__(self, connection):
        """
         If object creates first time - it will init everything
         If second time - it will use data from 1st time
        """
        if self.__is_initialized:
            print(f"Connection status: {self.__w3.isConnected()}")
        else:
            self.__set_new_connection(connection)	# add Web3
            self.__is_initialized = True				# to protect creation manager again

            self.__wallets = list()
            # Sets for fast search over wallets data
            self.__set_keys = set()
            self.__set_labels = set()
            self.__set_addr = set()
            self.__last_block = None  	# updates every N secs by daemon

            self._load_wallets()		# Load Wallets
            self.__load_txs()			# Load Txs
            self.__load_tokens()			# Load Tokens
            # Init sets if there are wallets
            if self.__wallets:
                print(texts.init_files, end=" ")
                self.update_wallets()
                self.__initialize_sets()
            print(texts.init_finished)

            # Start a demon to regularly update info (last block)
            threads.start_todo(self.__daemon_update_last_block, True)
            threads.start_todo(self.__daemon_update_gas, True)

    def __set_new_connection(self, connection: Web3):
        """Checks connection is Web3 and chain id is supported"""
        if not isinstance(connection, Web3):
            raise ValueError(texts.error_not_web3.format(connection, Web3))

        if connection.eth.chain_id not in settings.supported_chains:
            raise ValueError(texts.error_chain_not_supported.format(connection.eth.chain_id))
        
        self.__w3 = connection
        self.__chain_id = self.__w3.eth.chain_id
        print(texts.connected_to_rpc.format(self.__chain_id, settings.chain_name[self.__chain_id]))

########################################################################################################################
# Outer methods ########################################################################################################
########################################################################################################################

    def connection_status(self):
        is_connected = "Successfully connected" if self.__w3.isConnected() else "Failed to connect"
        print(f"{is_connected} to {settings.chain_name[self.__w3.eth.chain_id]}")

    def set_new_connection(self):
        self.__set_new_connection(assist.get_new_connection())
        self.update_wallets()
        
    def try_add_wallet(self):
        """
        Parses line and adds a wallet by private key
        We need TryExcept here to continue word if there's mistake with private key
        """
        while True:
            if len(self.__wallets) >= settings.max_wallets:
                raise PermissionError(texts.error_max_wallet_created.format(len(self.__wallets), settings.max_wallets))
            key = input(texts.input_private_key)
        
            try:
                assist.check_private_key(self.__set_keys, self.__wallets, key)
            except ValueError as e:
                print(e)
            else:
                wallet = Wallet(key)  # create Wallet
                if threads.can_create_daemon():
                    thread = threads.start_todo(self.update_wallet, True, wallet)
                    label = assist.ask_label(self.__set_labels)
                    thread.join()
                else:
                    label = assist.ask_label(self.__set_labels)
                    self.update_wallet(wallet)
            
                wallet.label = label
                self.__add_wallet(wallet)  # add wallet
                print(texts.added_wallet.format(wallet))

    def try_generate_wallets(self):
        try:
            print("> How many wallets you want to generate?")
            print("\t>> ", end="")
            number = int(input())
        except ValueError:
            print("> Wrong number", texts.exited, sep="\n")
            return
    
        max_allowed = settings.max_wallets
        created = len(self.__wallets)
        if created >= max_allowed:  # check Total Wallets less than Allowed in settings
            raise PermissionError(texts.error_max_wallet_created.format(created, max_allowed))
    
        allowed = max_allowed - created  # check is Allowed to create the amount user wants
        if number < 1 or number > allowed or number > settings.max_generate_addr:
            if allowed > settings.max_generate_addr:
                max_can_gen = settings.max_generate_addr
            else:
                max_can_gen = allowed
            print(texts.error_wrong_generate_number.format(allowed, created, max_allowed, max_can_gen, number))
            print(texts.exited)
        else:  # if Allowed - get the list with created wallets
            new_generated_wallets = assist.generate_wallets(self.__w3,
                                                            self.__set_labels.copy(),
                                                            self.__set_keys.copy(),
                                                            number)
            # add it to our list
            self.__add_wallets(new_generated_wallets)
        
            [print(wallet.addr, wallet.key()) for wallet in new_generated_wallets]
            print(f"> Generated {len(new_generated_wallets)} wallets")  # print generated wallets info

    def try_delete_wallet(self):
        """ Realisation of deleting wallets -> certain wallet, last, last N or all
        If change - be careful with .lower method !!
        """
        self.__check_wallets()
        to_delete = self.__print_ask(text_after=texts.instruction_to_delete_wallet,
                                     text_in_input=">> ")
        if not to_delete:
            print(texts.exited)
            return
    
        # Processing the input
        if to_delete.startswith("last"):  # if last - delete last
            self.__delete_last_N(to_delete)
        elif to_delete.startswith("first"):  # if first - delete first
            self.__delete_first_N(to_delete)
        elif to_delete == "all":  # if all - ask before deleting
            if assist.confirm():
                self.__delete_all()
                print(texts.success)
        else:  # else get wallets
            for wallet in self.__parse_wallets(to_delete):
                self.__delete_wallet(wallet)

    def try_send_transaction(self):
        self.__check_wallets()
        # Get sender
        sender_text = self.__print_ask(text_in_input="Choose wallet to send >> ")
        sender: Wallet = self.__parse_wallets(sender_text)[0]
        daemon1 = threads.start_todo(self.update_wallet, True, sender, False)
        daemon2 = None
    
        # Get what to send | returns Address for Erc20 or False for native coin
        it_is_erc20 = trans.send_erc20_or(self.__w3)
        if it_is_erc20:
            daemon2 = threads.start_todo(trans.update_erc_20, True, self.__w3, it_is_erc20)
    
        # Get receivers
        input_with_receivers = assist.print_ask(text_after=texts.choose_receivers, text_in_input="Your choice >> ")
        if input_with_receivers == "file":
            path = assist.print_ask(text_in_input=texts.get_path)
        
            try:
                receivers = assist.import_addrs(path)
            except FileNotFoundError:
                print("> Wrong file")
                return
        
            if not receivers:
                raise ValueError("> Didn't find correct addresses in the file")
            print("> Got", len(receivers), "addresses")
        else:
            receivers = self.__parse_wallets(users_input=input_with_receivers, delete_from_list=sender)
    
        daemon1.join()  # wait for daemon that updates sender
    
        if it_is_erc20:
            daemon2.join()
            token = assist.get_token(self.__w3, it_is_erc20)  # get SC token
            erc20 = self.__w3.eth.contract(address=token.sc_addr, abi=token.abi)  # connect to erc_20
        
            amount = trans.get_amount_for_erc20(erc20, token, sender, len(receivers))  # get amount to send
            # Ask for fee and send if Ok
            if not trans.print_price_and_confirm_erc20(token, erc20, sender, len(receivers), amount):
                raise InterruptedError(texts.exited)
            txs = trans.sender_erc20(erc20, token, sender, receivers, amount)
        else:
            amount_to_send = trans.get_amount_for_native(self.__w3, sender, receivers)
            # Ask for fee and send if Ok
            if not trans.print_price_and_confirm_native(self.__chain_id, value=amount_to_send,
                                                        receivers=len(receivers)):
                raise InterruptedError(texts.exited)
            txs = trans.sender_native(self.__w3, sender, receivers, amount_to_send)  # send txs
    
        # Last step - add all TXs to the list and print them
        [Manager.all_txs.append(tx) for tx in txs if tx not in Manager.all_txs]
        [print(tx) for tx in txs]
        
    def update_wallets(self, wallets: list = None):
        if wallets is None:
            wallets = self.__wallets
        
        assist.check_wallets(wallets)
        assist.update_wallets(self.__w3, wallets, self.__set_labels)

    def update_wallet(self, wallet, update_tx=True):
        """
        Updates received wallet:
        - balance
        - nonce
        - address, if the wallet doesn't have it
        - updates TX
        Updates TXs in the wallet which doesn't have status (Success/Fail)"""
        assist.update_wallet(self.__w3, wallet, self.__set_labels, update_tx)
        
    def export_wallets(self):
        self.__check_wallets()
        if assist.confirm(print_before="> Your data will be unprotected."):
            assist.export_wallets(self.__wallets)
            
    def import_wallets(self):
        path = assist.print_ask(text_in_input=texts.get_path)
        try:
            new_wallets = assist.import_wallets(path, self.__wallets, self.__set_keys, self.__set_labels)
        except FileNotFoundError:
            print("> Wrong path to the file\n", texts.exited)
            return

        if new_wallets:
            print("> Finished import. Updating...")
        else:
            print("> Finished. No wallets to import in the file.")

        # add it to our list
        self.update_wallets(new_wallets)  # update in multithreading
        self.__add_wallets(new_wallets)
        print(f"> Imported {len(new_wallets)} wallets")
        
    def change_label(self):
        wallets: list = self.__parse_wallets(self.__print_ask(text_in_input="Choose wallets >> "))
        if wallets:
            print("> Got {} wallets, lets rename them... ".format(len(wallets)))
        else:
            print(texts.exited)
        total = len(wallets)
        for i in range(total):
            instruction = "> {} / {}. How would you like to call it -> {}?".format(i, total, wallets[i])
            new = assist.ask_label(self.__set_labels, instruction=instruction)
            old = wallets[i].label
            wallets[i].label = new  # Add new label to Wallet
            self.__set_labels.add(new)  # Add new label to the Set
            self.__set_labels.remove(old)  # Delete old Label from the Set
            print(texts.change_label.format(old, new, wallets[i].addr))
        print(texts.exited)
        
    def delete_txs_history(self):
        """
        Deletes all saved TXs + clear txs list for each wallet
        """
        self.__check_txs()
        if assist.confirm():
            assist.delete_txs_history(self.__wallets)
            print(texts.success)
        
    def print_wallets(self):
        """Prints wallets with its index"""
        self.__check_wallets()
        assist.print_wallets(self.__wallets)

    def print_all_info(self):
        """Prints wallets with its index and TXs list"""
        self.__check_wallets()
        assist.print_all_info(self.__wallets)

    def print_all_txs(self):
        """Prints all TXs with current network (chain_id)"""
        self.__check_txs()
        assist.print_all_txs(self.__chain_id)

    def print_txs_for_wallet(self):
        """Prints TXs for selected wallet in current blockchain"""
        self.__check_wallets()
        self.__check_txs()
        text = self.__print_ask(text_after="Choose the acc:")  # prints wallets + ask to choose
        wallet = self.__wallets[self.__get_wallet_index(text)]
        assist.print_txs_for_wallet(self.__chain_id, wallet)  # prints txs for that wallet in the network

    def print_block_info(self, block_number=None):
        """
        Prints info about transferred block
        or the last block if block_number is None
        :param block_number: str or int of the block
        :return: nothing
        """
        # We have to know info about the last block
        if not self.__check_last_block():
            print(texts.error_no_info_about_last_block)
            return
    
        # We need to know that's the argument is not None. If None - use Last Block
        if block_number is None:
            block = self.__last_block
        else:
            # So we have argument, need to check it and get that block
            if block_number.isnumeric():
                block_number = int(block_number)
        
            # Check the asked block is smaller than the last one
            if block_number > self.__last_block["number"]:
                print(texts.error_block_doesnt_exist_yet)
                return
            else:
                block = self.__w3.eth.get_block(block_number)
    
        for k, v in block.items():  # get key and value
            print(k, end=" > ")  # print key, no \n
        
            if isinstance(v, bytes):  # if Value is bytes
                print(self.__w3.toHex(v))  # decode Value and print
            elif isinstance(v, list):  # if Value is list
                if not v:  # list empty - print \n
                    print()
                else:  # not empty
                    for el in v:  # decode and print all elements
                        print(self.__w3.toHex(el))
            else:  # if Value not list and not bytes - print it
                print(v)
                
########################################################################################################################
# Inner methods ########################################################################################################
########################################################################################################################

    def __initialize_sets(self):
        """Init sets with wallet info"""
        for wallet in self.__wallets:  		# for each wallet
            self.__add_to_sets(wallet)  		# add to sets

    def __add_to_sets(self, wallet):
        """Adds new wallet to sets if there's no such wallet.
        If there's same data - throws Exception"""
        # if any field in the set - throw error. Else - add new wallet
        if wallet.key() in self.__set_keys or wallet.label in self.__set_labels \
                                         or wallet.addr_lower in self.__set_addr:
            raise ValueError(texts.error_add_to_set)
        self.__set_keys.add(wallet.key())
        self.__set_labels.add(wallet.label)
        self.__set_addr.add(wallet.addr_lower)

    def __delete_from_sets(self, wallet):
        """ Deletes wallet from the sets if every field is in sets. Otherwise, throws Exception """
        if wallet.key() not in self.__set_keys or wallet.label not in self.__set_labels \
                                             or wallet.addr_lower not in self.__set_addr:
            raise ValueError(texts.error_delete_from_set)
        self.__set_keys.remove(wallet.key())
        self.__set_labels.remove(wallet.label)
        self.__set_addr.remove(wallet.addr_lower)

    def __add_wallets(self, wallets: list):
        for wallet in wallets:
            self.__add_wallet(wallet)

    def __add_wallet(self, wallet: Wallet):
        """Adds wallet into the list and sets"""
        assist.check_wallet_type(wallet)
        if not wallet.addr:						# if no addr
            self.update_wallet(wallet)			# get it

        self.__wallets.append(wallet)			# add to the list
        self.__add_to_sets(wallet)				# add to the sets

    def __delete_wallet(self, index_or_wallet):
        """
        Deletes wallet from list and sets by its Index in the list or Wallet obj
        :param index_or_wallet: wallet Index in the list OR wallet Obj in the list
        """
        if isinstance(index_or_wallet, Wallet):  # if it's wallet - get it's index
            index = self.__get_wallet_index(index_or_wallet)
        else:
            index = index_or_wallet
            
        if not isinstance(index, int):
            raise TypeError("It's not wallet or index, I don't work with it. Tell the devs")

        wallet = self.__wallets.pop(index)      # del from the list
        self.__delete_from_sets(wallet)         # del from the sets
        print(texts.deleted_successfully, wallet.addr)
        del wallet

    def __delete_first_N(self, line):
        """Deletes N first wallets
        :param line: str that starts on "first..."
        """
        if line == "first":                 # if first - delete first
            self.__delete_wallet(0)
        else:                               # if more:
            amount = int(line.split()[1])   # parse amount
            if amount > len(self.__wallets):
                raise IndexError(texts.del_out_of_index)
            
            for _ in range(amount):         # delete them
                self.__delete_wallet(0)

    def __delete_last_N(self, line):
        """Deletes N last wallets
        :param line: str that starts on "last..." """
        if line == "last":                  # if last - delete it
            self.__delete_wallet(len(self.__wallets) - 1)
        else:                               # if more:
            amount = int(line.split()[1])  	# parse amount
            if amount > len(self.__wallets):
                raise IndexError(texts.del_out_of_index)
            
            for _ in range(amount):         # delete them
                self.__delete_wallet(len(self.__wallets) - 1)

    def __delete_all(self):
        """Deletes all wallets, use with careful"""
        self.__wallets.clear()
        self.__set_addr.clear()
        self.__set_labels.clear()
        self.__set_keys.clear()
        
    def __get_wallet_index(self, text: str | Wallet) -> int:
        """Returns index of the wallet in the list from:
         - Wallet
         - Text (number, address or label)"""
        return assist.get_wallet_index(text, self.__wallets, self.__set_addr, self.__set_labels)

    def __parse_wallets(self, users_input: str, delete_from_list: Wallet | list = None):
        """
        Receive input and parse list of wallets from it. Deletes wallet / wallets if received in delete_from_list
        :param users_input: string with selected wallet(s)
        :param delete_from_list: Wallet obj or list with (Wallet obj, address or label or number of wallets in system)
        :return: list with wallets
        """
        if users_input == "all":                # if all -> get all wallets
            wallets = self.__wallets.copy()
        else:
            wallets = set()                     # or parse from line and add
            for text in users_input.split():    # with deleting duplicates
                index = self.__get_wallet_index(text)
                wallets.add(self.__wallets[index])
    
        if isinstance(delete_from_list, Wallet):    # delete 1 wallet
            if delete_from_list in wallets:
                wallets.remove(delete_from_list)
        elif isinstance(delete_from_list, list):    # or delete barch of wallets
            for wallet in delete_from_list:
                if wallet in wallets:
                    wallets.remove(wallet)
    
        return list(wallets)  # return asked wallets

    def __check_wallets(self):
        assist.check_wallets(self.__wallets)
    
    @staticmethod
    def __check_txs():
        if not Manager.all_txs:
            raise ValueError(texts.no_txs)

    def __print_ask(self, text_before=None, text_after=None, text_in_input=None) -> str:
        """
        Prints wallets and text if given, asks to input text.
        If empty - make exit, if not - return text
        -> Use this when you need to print wallets.
            (if you don't want to print -> use assist.print_ask())"""
        return assist.print_ask(self.__wallets, text_before=text_before, text_after=text_after,
                                text_in_input=text_in_input)

    def __check_last_block(self) -> bool:
        """
        Checks that the last block is exist.
        If it doesn't exist - tries to update it
        :return: True or False
        """
        if self.__last_block is not None:  # exist - Ok, tell it
            return True
        else:  # No?
            print("No info about the last block, updating...")
            self.__update_last_block()  # Try to update
    
            if self.__last_block is not None:  # if not Ok - tell it
                print(texts.success)
                return True
            else:
                print(texts.fail)  # no? - So sad...
                return False
        
    def __update_last_block(self):
        self.__last_block = self.__w3.eth.get_block("latest")
        
    def __daemon_update_last_block(self):
        """Daemon updates block even N secs"""
        while True:
            self.__update_last_block()  # update
            time.sleep(settings.update_block_every)  # sleep
            logs.pr_daemon(f"Daemon, updated the last block, current block is {self.__last_block['number']}")

    def __daemon_update_gas(self):
        """Daemon updates gas price & max priority every N secs. Very important info, change with care"""
        while True:		# no change int !! That's wei, so Ok. And web3 doesn't work with float.
            Manager.network_gas_price = self.__w3.eth.gas_price
            Manager.network_max_priority = self.__w3.eth.max_priority_fee

            Manager.gas_price = int(Manager.network_gas_price * settings.multiply_gas_price)
            Manager.max_priority = int(Manager.network_max_priority * settings.multiply_priority)

            min_gas = Web3.toWei(settings.min_gas_price, "gwei")		# change gas to min if current < min
            if Manager.gas_price < min_gas:
                Manager.gas_price = min_gas

            min_priority = Web3.toWei(settings.min_priority, "gwei")	# same with priority
            if Manager.max_priority < min_priority:
                Manager.max_priority = min_priority
            time.sleep(settings.update_gas_every)

########################################################################################################################
# Save-Load ####### probably it should be changed with decorators.. code is the same, except file, text and vars #######
########################################################################################################################

    def _save_wallets(self):
        assist.save_data(self.__wallets, settings.folder, settings.saved_wallets)

    def _load_wallets(self):
        print(texts.loading_wallets, end=" ")  		# Start
        loaded_data = assist.load_data(settings.folder, settings.saved_wallets)
        if loaded_data is None:
            print(texts.no_wallets_to_load)			# End - Tell no wallets to load
        else:
            self.__wallets = loaded_data
            print(texts.success)  					# End - Success

    @staticmethod
    def __save_tokens():
        assist.save_data(Manager.all_tokens, settings.folder, settings.saved_tokens)

    @staticmethod
    def __load_tokens():
        print(texts.loading_tokens, end=" ")  # Start
        loaded_data = assist.load_data(settings.folder, settings.saved_tokens)
        if loaded_data is None:
            print(texts.no_tokens_to_load)  # End - Tell no tokens to load
        else:
            Manager.all_tokens = loaded_data
            print(texts.success)  # End - Success

    @staticmethod
    def __save_txs():
        assist.save_data(Manager.all_txs, settings.folder, settings.saved_txs)

    @staticmethod
    def __load_txs():
        print(texts.loading_txs, end=" ")  # Start
        loaded_data = assist.load_data(settings.folder, settings.saved_txs)
        if loaded_data is None:
            print(texts.no_txs_to_load)  # End - Tell no txs to load
        else:
            Manager.all_txs = loaded_data
            print(texts.success)  # End - Success

########################################################################################################################
# Finish ###############################################################################################################
########################################################################################################################

    def finish_work(self):
        """
        Saving all data before finishing the work.
        BE CAREFUL!!
        In current realisation for the correct operation of the program
        > TXs should be saved and then deleted from wallets BEFORE saving Wallets.
        > If not - for next loading wallets will be loaded with
            duplicated TXs inside
        """
        self.__save_txs()
        self.__save_tokens()
        assist.delete_txs_history(self.__wallets)		# Delete tx_list (+ txs from wallets)
        self._save_wallets()