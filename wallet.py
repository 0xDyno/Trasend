class Wallet:

    nonce = int()
    address = str()
    balance_in_wei = int()


    def get_all_info(self):
        format_ = "%s: %s (balance: %.4f ETH)"
        return format_ % (self.label, self.address, self.get_eth_balance())


    def get_private_key(self):
        return self.__key

    def get_eth_balance(self):
        return self.balance_in_wei / 10**18

    def __init__(self, private_key, label):
        self.__key = private_key
        self.label = label

    def __str__(self):
        return self.get_all_info()

    def __repr__(self):
        return self.__str__()