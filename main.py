import services.classes
from services import assist
from services.manager import Manager
from config.text import main_text_instruction, success
from web3 import Web3
import config.keys


def main():
    print("\n%s\n---------------------" % main_text_instruction)
    while True:
        text = input().lower()
        match text:
            case "1":                                                                       # Show all wallets
                m.print_wallets()
            case "1a":                                                                      # Show all wallets + trans
                m.print_all_info()
            case "1t":                                                                      # Show all TXs
                m.print_all_txs()
            case "2":                                                                       # Add wallets
                m.try_add_wallet()
            case "2g":                                                                      # Generate wallets
                number = input("How many wallets generate? (up to 100) >>> ")
                if number.isnumeric():
                    m.generate_wallets(int(number))
                else:
                    print("Not a number")
            case "3":                                                                       # Delete wallets
                m.try_delete_wallet()
            case "3l":                                  # to change
                pass
            case "3a":                                                                      # Delete all
                if assist.confirm():
                    m.delete_all()
            case "3t":                                                                      # Delete all transactions
                if assist.confirm():
                    m.delete_txs_history()
                    print(success)
            case "4":                                                                       # Send transaction (main co)
                m.try_send_transaction()
            case "4all":                                # to implement Send to All wallets
                pass
            case "4e":                                  # to implement Send ERC-20
                pass
            case "5":                                                                       # empty
                pass
            case "6":                                                                       # empty
                pass
            case "7":                                                                       # empty
                pass
            case "8":                                                                       # empty
                pass
            case "9":                                                                       # empty
                pass
            case "upd":                                                                     # last block info
                m.update_wallets()
            case "01":                                                                      # check connection
                m.print_block_info()
            case "02":                                                                      # update wallets
                m.connection_status()
            case "t":                                                                       #
                for w in m.wallets:
                    txs = w.txs
                    print(len(txs), txs)
            case "exit":                                                                    #
                break
            case "e":
                break
            case "":
                pass
            case _:
                print("Wrong command. Try again.")
        print("\n%s\n---------------------" % main_text_instruction)


if __name__ == "__main__":
    print("Trying to connect RPC point (node)...", end=" ")
    connection = Web3(Web3.HTTPProvider(config.keys.HTTPS_GOERLI))
    print("success")
    m = Manager(connection)

    try:
        main()
    except KeyboardInterrupt:
        print("Exited by Keyboard Interruption")
    finally:
        m.finish_work()
else:
    print("I won't work like that. You have to start the app directly from it's main file")