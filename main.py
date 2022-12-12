import threading

from services.manager import Manager
from services.trans import print_gas_price_info
from services import assist
from config.texts import main_text_instruction, success
from config.settings import max_generate_addr
from config.keys import HTTPS_GOERLI, HTTPS_ETH

from web3 import Web3


def main():
    print("\n%s\n---------------------" % main_text_instruction)
    while True:
        text = input().lower().strip()
        match text:
            case "1":                                                                       # Show all wallets
                m.print_wallets()
            case "1a":                                                                      # Show all wallets + trans
                m.print_all_info()
            case "1t":                                                                      # Show all TXs
                m.print_all_txs()
            case "1at":                                                                     # Show all TXs for 1 acc
                m.print_txs_for_wallet()
            case "2":                                                                       # Add wallets
                m.try_add_wallet()
            case "2g":                                                                      # Generate wallets
                number = input(f"How many wallets generate? (up to {max_generate_addr}) >>> ")
                if number.isnumeric():
                    m.generate_wallets(int(number))
                else:
                    print("Not a number")
            case "3":                                                                       # Delete wallets
                m.try_delete_wallet()
            case "3a":                                                                      # Delete all
                if assist.confirm():
                    m.delete_all()
                    print(success)
            case "3t":                                                                      # Delete all transactions
                if assist.confirm():
                    m.delete_txs_history()
                    print(success)
            case "4":                                                                       # Send transaction (native)
                m.try_send_transaction()
            case "4a":                                                                      # Send to All (native)
                m.try_send_to_all()
            case "4e":                                  # to implement Send ERC-20
                pass
            case "4ea":                                 # to implement Send ETC-20 to All
                pass
            case "5":                                                                       # empty
                pass
            case "upd":                                                                     # last block info
                m.update_wallets()
            case "01":                                                                      # check connection
                m.print_block_info()
            case "02":                                                                      # update wallets
                m.connection_status()
            case "03":
                print_gas_price_info()
            case "t":       # print txs in every wallet
                for w in m.wallets:
                    txs = w.txs
                    print(len(txs), txs)
            case "th":      # print total threads
                print(len(threading.enumerate()), " : ", threading.enumerate())
            case "exit":
                break
            case "e":
                break
            case "h":
                print("\n%s\n---------------------" % main_text_instruction)
            case _:
                print("Wrong command. If you need instruction - print h")


if __name__ == "__main__":
    print("Trying to connect RPC point (node)...", end=" ")
    connection = Web3(Web3.HTTPProvider(HTTPS_GOERLI))
    print("success")
    m = Manager(connection)

    try:
        main()
    except KeyboardInterrupt:
        print("Finished")
    finally:
        m.finish_work()
else:
    print("I won't work like that. You have to start the app directly from it's main file")