class Wallet:

    nonce = int()
    address = str()
    balance = float()


    def get_all_info(self):
        if self.balance is int():
            return "%s: %s, balance: %d ETH" % (self.label, self.address, self.balance)
        else:
            return "%s. %s, balance: %.4f ETH" % (self.label, self.address, self.balance)


    def get_private_key(self):
        return self.__private_key

    def __init__(self, private_key, label):
        self.__private_key = private_key
        self.label = label

    def __str__(self):
        return self.get_all_info()

    def __repr__(self):
        return self.__str__()