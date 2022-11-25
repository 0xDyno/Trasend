from manager import Manager
from web3 import Web3
from config  import keys


def start():
    pass


def main():
    for addr in m.list_with_wallets:
        print(addr.get_all_info())


def end():
    m.save_wallets_list()


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider(keys.HTTPS))
    m = Manager(w3)

    # The app is running
    main()

    # Finish the app
    end()
else:
    print("Nope")






# def check_save():
#     wal1 = Wallet(label="Someone's address",
#                        address="0x9f4b4ceca7ace96834bd2fcc961c772de7cb481a",
#                        private_key="x3")
#     wal2 = Wallet(label="Bitpie 1",
#                         address="0xf64edD94558Ca8B3a0e3b362e20BB13ff52eA513",
#                         private_key="x3")
#     wal3 = Wallet(label="Centre: USD Coin",
#                         address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
#                         private_key="x3")
#     list_of_addresses = [wal1, wal2, wal3]
#
#     print(f"Loaded from the app: \n{id(list_of_addresses)} : {list_of_addresses}")
#     print("\n--\n")
#
#     print("Saved...")
#     save_list_of_addresses(list_of_addresses)       # Save
#     print("Recovered...")
#     new_list = get_list_of_addresses()              # Recover
#     print(f"{id(new_list)} : {new_list}")