class Wallet:

    def get_all_info(self):
        return f"{self.label} : {self.address} : {self.mnemonic} : {self.private_key}"

    def __init__(self, address, label="None", mnemonic="None", private_key="None"):
        self.label = label
        self.address = address
        self.mnemonic = mnemonic
        self.private_key = private_key

    def __str__(self):
        if self.label != "None":
            return f"{self.label}: {self.address}"
        else:
            return f"Address {self.address}"

    def __repr__(self):
        return self.__str__()