from manager import Manager
from web3 import Web3
from config  import keys
from config.settings import instruction


def main():
    print("%s\n" % instruction)
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
        print("\n%s\n" % instruction)


def end():
    m.save_wallets_list()


if __name__ == "__main__":
    m = Manager(Web3(Web3.HTTPProvider(keys.HTTPS)))
    # The app is running
    main()
    # Save data
    end()
else:
    print("Nope")