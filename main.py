import eth_account.signers.local
import web3

import config.keys
from manager import Manager
from web3 import Web3
from config.settings import *


def main():
    print("%s\n---------------------" % instruction)
    while text := input("").lower():
        match text:
            case "1":
                for wallet in m.list_with_wallets:
                    print(wallet)
            case "2":
                m.add_wallet()
            case "3":
                m.delete_wallet()
            case "4":
                print(f"Connection status: {m.connection.isConnected()}")
            case "exit":
                break
            case _:
                print("Wrong command. Try again.")
        print("\n%s\n---------------------" % instruction)



def end():
    m.save_wallets_list()


def test():
    print(Web3.isAddress("0x55A1237c375b2a0F87e7e5CD0D782005844F771B"))
    print(m.connection.eth.get_balance("0x55A1237c375b2a0F87e7e5CD0D782005844F771B"))
    res: eth_account.signers.local.LocalAccount = web3.Account.privateKeyToAccount("0xbeef2eea6c075377eb78100fa682df3aa46cdcaeb4f09d68482c74f1679bd3ca")
    print(res, type(res))
    print(res.address)
    print(res.key)



if __name__ == "__main__":
    m = Manager(Web3(Web3.HTTPProvider(config.keys.HTTPS)))
    # The app is running
    # main()
    test()
    # Save data
    end()
else:
    print("Nope")