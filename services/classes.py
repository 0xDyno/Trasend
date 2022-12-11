from datetime import datetime
import webbrowser

from config import text
from config.settings import chain_explorers, chain_default_token
from web3 import Web3


class Wallet:
    def __init__(self, private_key, label):
        self._key = private_key
        self.label = label

        self.nonce = int()
        self.addr = str()
        self.balance_in_wei = int()
        self.txs = list()               # list with Transaction objects

    def __str__(self):
        return self.get_info()

    def __repr__(self):
        return self.__str__()

    def get_info(self):
        format_ = "%s. %s (balance: %.4f ETH)"
        return format_ % (self.label, self.addr, self.get_eth_balance())

    def get_all_info(self):
        line = self.get_info()
        if self.txs:
            line += "\nTransactions:"
            for tx in self.txs:
                line += "\n\t" + self.get_transaction_info(tx)
        else:
            line += " -- no transactions"

        return line

    def key(self):
        return self._key

    def get_eth_balance(self):
        return Web3.fromWei(self.balance_in_wei, "ether")

    def print_transactions(self):
        for tx in self.txs:
            print(self.get_transaction_info(tx))

    def get_transaction_info(self, tx):
        tx_type = tx.get_tx_type(self)      # get type Received or Sent
        tx_time = tx.get_time()             # get date

        if tx_type == text.tx_received:
            sender_or_receiver = "from " + tx.sent_from.addr
        else:
            sender_or_receiver = "to " + tx.sent_to.addr
        link = chain_explorers[tx.chainId] + tx.tx
        blockchain = chain_default_token[tx.chainId]

        format_ = "{blockchain} >> {tx_type} {value} {token} {sender_or_receiver} on {date}\n\t\t{status} >>> {link}"

        return format_.format(blockchain=blockchain, tx_type=tx_type, value=tx.get_eth_value(), token=tx.which_token,
                            sender_or_receiver=sender_or_receiver, date=tx_time, status=tx.status, link=link)


class Transaction:


    def __init__(self, chainId: int, time: float, sent_to: Wallet,
                 sent_from: Wallet, value: str, tx: str, token=None):
        """
        :param chainId: chainId
        :param time: usual time is secs
        :param sent_to: sent to Wallet obj
        :param sent_from: sent from Wallet obj
        :param value: sent amount
        :param tx: tx_hash text
        :param token: Ticker of smart-contract, None if default network (ETH, BNB, MATIC etc)
        """
        self.chainId = chainId                          # _1
        self.date = datetime.fromtimestamp(time)        # _2 -- datetime
        self.status = None                              # _3 -- Success / Fail / None
        self.sent_to = sent_to                          # _4 to
        self.sent_from = sent_from                      # _5 from
        self.value = value                              # _6 value
        self.which_token = bool                         # _7 Main token or TokenTicket
        self.tx = tx                                    # _8 transaction hash
        if token is None:
            self.which_token = chain_default_token[chainId]
        else:
            self.which_token = token

        # Add to wallets
        self.sent_to.txs.append(self)
        self.sent_from.txs.append(self)

    def __str__(self):
        line = "{blockchain} bc >> From {sender} sent {amount} {token} to {receiver} on {date}" + \
               "\n\tStatus {status}, link: "
        blockchain = chain_default_token[self.chainId]
        link = chain_explorers[self.chainId] + self.tx
        return line.format(blockchain=blockchain,
                           sender=self.sent_from.addr,
                           amount=Web3.fromWei(self.value, "ether"),
                           token=self.which_token,
                           receiver=self.sent_to.addr,
                           date=self.get_time(),
                           status=self.status) + link

    def __eq__(self, other):
        return self.tx == other.tx

    def __hash__(self):
        return hash(self.tx)

    def get_eth_value(self):
        return Web3.fromWei(self.value, "ether")

    def get_tx_type(self, wallet: Wallet):
        if self.sent_to.addr == wallet.addr:
            return text.tx_received
        else:
            return text.tx_sent

    def get_time(self):
        return str(datetime.strftime(self.date, "%d.%m.%Y %H:%M:%S"))

    def open_explorer(self):
        webbrowser.open(chain_explorers[self.chainId] + self.tx)

    def delete(self):
        if self in self.sent_to.txs:
            index = self.sent_to.txs.index(self)
            self.sent_to.txs.pop(index)
        if self in self.sent_from.txs:
            index = self.sent_from.txs.index(self)
            self.sent_from.txs.pop(index)