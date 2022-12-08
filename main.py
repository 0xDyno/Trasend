from web3 import Web3
from manager import Manager
from config.text import main_text_instruction
import config.keys


def main():
    print("\n%s\n---------------------" % main_text_instruction)
    while True:
        text = input().lower()
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
                print(f"Connection status: {m.web3.isConnected()}")
            case "6":
                m.update_wallets()
            case "7":
                m.print_block_info()
            case "8":   # Send Transaction
                pass
            case "9":   # ??
                pass
            case "t":
                pass
                # key = Fernet.generate_key()
                # with open("crypto.key", "wb") as w:
                #     w.write(key)
            case "exit":
                break
            case "e":
                break
            case "":
                pass
            case _:
                print("Wrong command. Try again.")
        print("\n%s\n---------------------" % main_text_instruction)


if __name__ == "__main__":
    m = Manager(Web3(Web3.HTTPProvider(config.keys.HTTPS_GOERLI)))

    try:
        main()
    except KeyboardInterrupt:
        print("Exited by Keyboard Interruption")
    finally:
        m.finish_work()
else:
    print("I won't work like that. You have to start the app directly from it's main file")