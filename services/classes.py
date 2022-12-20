from datetime import datetime
import webbrowser

from web3 import Web3

from config import texts, settings


class Wallet:
    def __init__(self, private_key, label=None):
        """
        Pay attention to addr and addr_lower. First one with big letters, it should be used to print and
        send TXs. Second one is used to work with object, compare, search in sets, find etc..
        """
        self.__key = private_key
        self.label = label

        self.nonce = int()
        self.addr = str()               # - CheckSum addr, use to print / send TXs
        self.addr_lower = str()         # - use to compare / find
        self.balance_in_wei = int()
        self.txs = list()               # list with Transaction objects

    def __str__(self):
        length = str(settings.label_max_length + 1)
        format_ = "{:<" + length + "} {} (balance: {:.4f} ETH)"
        
        balance = self.get_eth_balance()
        return format_.format(self.label, self.addr, float(balance))

    def __repr__(self):
        return f"{id(self)} - Wallet obj - addr {self.addr}"

    def get_all_info(self):
        line = self.__str__()           # all info
        if self.txs:                    # + all transactions if there are
            line += " | TXs:"
            for tx in self.txs:
                line += "\n --- " + self.get_transaction_info(tx)
        else:
            line += " | no tx"

        return line

    def key(self):
        return self.__key

    def get_eth_balance(self):
        return Web3.fromWei(self.balance_in_wei, "ether")

    def print_transactions(self):
        for tx in self.txs:
            print(self.get_transaction_info(tx))

    def get_transaction_info(self, tx):
        tx_type = tx.get_tx_type(self)      # get type Received or Sent
        tx_time = tx.get_time()             # get date

        if tx_type == texts.tx_received:     # self - is receiver or sender?
            sender_or_receiver = "from " + tx.sender
        else:
            sender_or_receiver = "to " + tx.receiver
        link = settings.chain_explorers[tx.chain_id] + "tx/" + tx.tx      # get explorer + tx = link
        blockchain = settings.chain_name[tx.chain_id]

        format_ = "({blockchain}) {status}: {tx_type} {value} {token} {sender_or_receiver} on {date} ({link})"

        return format_.format(blockchain=blockchain, tx_type=tx_type, value=tx.value, token=tx.symbol,
                              sender_or_receiver=sender_or_receiver, date=tx_time, status=tx.status, link=link)


class Transaction:
    def __init__(self, chain_id: int, time: float, receiver: Wallet | str,
                 sender: Wallet | str, value: str, tx: str, token=None, sc_addr: str = None):
        """
        :param chain_id: chain_id
        :param time: usual time is secs
        :param receiver: addr str
        :param sender: addr str
        :param value: sent amount
        :param tx: tx_hash text
        :param token: Ticker of smart-contract, None if default network (ETH, BNB, MATIC etc)
        :param sc_addr: smart contract address for ERC-20
        """
        if token is None:
            self.symbol = settings.chain_default_coin[chain_id]
        else:
            self.symbol = token
            if sc_addr is None or not sc_addr.startswith("0x") or len(sc_addr) != settings.address_length:
                raise TypeError("Can't create TX, wrong Smart-Contract Address: ", sc_addr)
            self.address = sc_addr

        self.chain_id = chain_id                        #_1
        self.date = datetime.fromtimestamp(time)        #_2 -- datetime
        self.status = None                              #_3 -- Success / Fail / None
        self.value = value                              #_6 value
        self.tx = tx                                    #_7 transaction hash

        if isinstance(receiver, Wallet):
            receiver.txs.append(self)
            self.receiver = receiver.addr   # _4 to
        else:
            self.receiver = receiver        # _4 to
        if isinstance(sender, Wallet):
            sender.txs.append(self)
            self.sender = sender.addr       #_5 from
        else:
            self.sender = sender            #_5 from

    def __str__(self):
        return settings.chain_name[self.chain_id] + " >> " + self.str_no_bc()

    def str_no_bc(self):
        """Returns text with no BlockChain info"""
        string = "From {sender} sent {amount} {token} to {receiver} on {date}\n\t\t{status}, link: {link}"
        link = settings.chain_explorers[self.chain_id] + "tx/" + self.tx
        return string.format(sender=self.sender, amount=self.value, token=self.symbol, receiver=self.receiver,
                             date=self.get_time(), status=self.status, link=link)

    def get_tx_type(self, wallet: Wallet):
        """Returns the wallet is sender or receiver"""
        if self.receiver == wallet.addr:
            return texts.tx_received
        else:
            return texts.tx_sent

    def get_time(self):
        return str(datetime.strftime(self.date, "%d.%m.%Y %H:%M:%S"))

    def open_explorer(self):
        webbrowser.open(settings.chain_explorers[self.chain_id] + self.tx)


class Token:
    def __init__(self, chain_id: int, sc_addr: str, symbol: str, decimal: int, abi):
        if sc_addr is None or not sc_addr.startswith("0x") or len(sc_addr) != settings.address_length:
            raise TypeError("Can't create TX, wrong Smart-Contract Address: ", sc_addr)
        
        self.chain_id = chain_id
        self.sc_addr = Web3.toChecksumAddress(sc_addr)
        self.symbol = symbol
        self.decimal = decimal
        self.abi = abi

    def __str__(self):
        chain = settings.chain_default_coin[self.chain_id]
        format_ = "({chain}) {sym} - {addr} - {dec}"
        return format_.format(chain, self.symbol, self.sc_addr, self.decimal)