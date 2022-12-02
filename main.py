import eth_account.signers.local
import web3
from web3 import Web3
from manager import Manager
from config.settings import main_text_instruction
import config.keys


def main():
    print("\n%s\n---------------------" % main_text_instruction)
    while text := input("").lower():
        match text:
            case "1":
                m.print_wallets()
            case "2":
                m.add_wallet()
            case "3":
                number = input("How many wallets generate? (up to 100) >>> ")
                if number.isnumeric():
                    m.generate_wallets(int(number))
                else:
                    print("Not a number")
            case "4":
                m.delete_wallet()
            case "5":
                print(f"Connection status: {m.connection.isConnected()}")
            case "6":
                m.update_wallets()
                print("Successfully updated")
            case "exit":
                break
            case _:
                print("Wrong command. Try again.")
        print("\n%s\n---------------------" % main_text_instruction)



def end():
    m.save_wallets_list()


def test():
    pass


if __name__ == "__main__":
    # m = Manager(Web3(Web3.HTTPProvider(config.keys.HTTPS_ETH)))
    m = Manager(Web3(Web3.HTTPProvider(config.keys.HTTPS_GOERLI)))

    try:
        # The app is running
        main()

        # test()
    except KeyboardInterrupt:
        print("Exited by Keyboard Interruption")
    finally:
        # Save data
        end()
else:
    print("Nope")