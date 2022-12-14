import threading

from config import texts
from services.manager import Manager
from services.trans import print_gas_price_info
from services import assist
from config.keys import HTTPS_GOERLI, HTTPS_ETH

from web3 import Web3


def main():
    print("\n%s\n---------------------" % texts.instruction_main)
    while True:
        try:
            text = input().lower().strip()
            match text:
                case "1":                                                                   # Show all wallets
                    m.print_wallets()
                case "1a":                                                                  # Show all wallets + trans
                    m.print_all_info()
                case "1t":                                                                  # Show all TXs
                    m.print_all_txs()
                case "1at":                                                                 # Show all TXs for 1 acc
                    m.print_txs_for_wallet()
                case "2":                                                                   # Add wallets
                    m.try_add_wallet()
                case "2g":                                                                  # Generate wallets
                    m.try_generate_wallets()
                case "3":                                                                   # Delete wallets
                    m.try_delete_wallet()
                case "3a":                                                                  # Delete all
                    if assist.confirm():
                        m.delete_all()
                        print(texts.success)
                case "3t":                                                                  # Delete all transactions
                    if assist.confirm():
                        m.delete_txs_history()
                        print(texts.success)
                case "4":                                                                   # Send transaction (native)
                    m.try_send_transaction()
                case "4a":                                                                  # Send to All (native)
                    # m.try_send_to_all()
                    pass
                case "4e":                              # to implement Send ERC-20
                    pass
                case "4ea":                             # to implement Send ETC-20 to All
                    pass
                case "5":                                                                   # empty
                    pass
                case "upd":                                                                 # last block info
                    m.update_wallets()
                case "01":                                                                  # check connection
                    m.print_block_info()
                case "02":                                                                  # update wallets
                    m.connection_status()
                case "03":
                    print_gas_price_info()
                case "t":       # print txs in every wallet
                    for w in m.wallets:
                        txs = w.txs
                        print(len(txs), txs)
                case "th":       # print total threads
                    print(len(threading.enumerate()), " : ", threading.enumerate())
                case "tset":
                    print("Addrs:")
                    [print(addr, end=" ") for addr in m.set_addr]
                    print("\nKeys:")
                    [print(key, end=" ") for key in m.set_keys]
                    print("\nLabels:")
                    [print(label, end=" ") for label in m.set_labels]
                    print("\n")
                case "exit":
                    break
                case "e":
                    break
                case "h":
                    print("\n%s\n---------------------" % texts.instruction_main)
                case _:
                    print(texts.wrong_command_main)
        except (AssertionError, TypeError, IndexError, InterruptedError) as e:
            print(e)
        except KeyboardInterrupt:
            print("Finished")
            break


if __name__ == "__main__":
    print(texts.trying_connect, end=" ")
    connection = Web3(Web3.HTTPProvider(HTTPS_GOERLI))
    print(texts.success)
    m = Manager(connection)

    try:
        main()
    finally:
        m.finish_work()
else:
    print("I won't work like that. You have to start the app directly from it's main file")