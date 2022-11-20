from wallet import *
from tools import *
from get_addresses import get_the_dict_with_addresses


def check_save():
    wal1 = Wallet(label="Someone's address",
                       address="0x9f4b4ceca7ace96834bd2fcc961c772de7cb481a",
                       private_key="x3")
    wal2 = Wallet(label="Bitpie 1",
                        address="0xf64edD94558Ca8B3a0e3b362e20BB13ff52eA513",
                        private_key="x3")
    wal3 = Wallet(label="Centre: USD Coin\t",
                        address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                        private_key="x3")
    list_of_addresses = [wal1, wal2, wal3]

    print(f"{id(list_of_addresses)} : {list_of_addresses}")
    print("\n--\n")

    # Какой вариант сохранения использовать - меняется в tools
    if not use_old_version:                             # Use NEW Version
        save_list_of_addresses(list_of_addresses)       # Save
        new_list = get_list_of_addresses()              # Recover
        print(f"{id(new_list)} : {new_list}")
    else:                                           # Use OLD Version
        save_list_of_addresses_old(list_of_addresses)   # Save
        new_list = get_list_of_addresses_old()          # Recover
        print(f"{id(new_list)} : {new_list}")


def main():
    pass


if __name__ == "__main__":
    main()
