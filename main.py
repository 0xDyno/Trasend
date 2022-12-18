import threading

from urllib3.exceptions import MaxRetryError, NewConnectionError

import config.settings
from config import texts
from services.manager import Manager
from services.trans import print_gas_price_info
from services import assist
from config.keys import HTTPS_GOERLI, HTTPS_ETH

from web3 import Web3


def main():
    print("\n%s\n" % texts.instruction_main)
    while True:
        try:
            text = input("  >>> ").lower().strip()
            match text:
                case "1":                             # Show all wallets
                    m.print_wallets()
                case "1a":                            # Show all wallets + trans
                    m.print_all_info()
                case "1t":                            # Show all TXs
                    m.print_all_txs()
                case "1at":                           # Show all TXs for 1 acc
                    m.print_txs_for_wallet()
                case "2":                             # Add wallets
                    m.try_add_wallet()
                case "2g":                            # Generate wallets
                    m.try_generate_wallets()
                case "2e":                            # Export wallet
                    m.export_wallets()
                case "2i":
                    m.import_wallets()
                case "3":                             # Delete wallets
                    m.try_delete_wallet()
                case "3t":                            # Delete all transactions
                    m.delete_txs_history()
                case "4":                             # Send transaction (native)
                    m.try_send_transaction()
                case "5":                             # empty
                    pass
                case "upd":                           # update wallets
                    m.update_wallets()
                case "label":                         # change label
                    m.change_label()
                case "01":                            # last block info
                    m.print_block_info()
                case "02":                            # check connection
                    m.connection_status()
                case "03":
                    print_gas_price_info()
                case "t":       # print txs in every wallet
                    pass
                case "th":       # print total threads
                    print(len(threading.enumerate()), " : ", threading.enumerate())
                case "tt":
                    for token in Manager.all_tokens:
                        chain = config.settings.chain_name[token.chain_id]
                        print("{}: {} {} {}".format(chain, token.symbol, token.sc_addr, token.decimal))
                case "tset":
                    pass
                case "exit":
                    break
                case "e":
                    break
                case "h":
                    print("\n%s\n---------------------" % texts.instruction_main)
                case _:
                    print(texts.wrong_command_main)
        except (AssertionError, TypeError, IndexError, ValueError, InterruptedError) as e:
            print(e)
        except (ConnectionError, MaxRetryError, NewConnectionError):
            print("Error with connection. Probably you don't have internet connection.")
        except KeyboardInterrupt:
            print("Finished")
            break


if __name__ == "__main__":
    try:
        print(texts.trying_connect, end=" ")
        connection = Web3(Web3.HTTPProvider(HTTPS_ETH))
        print(texts.success)
        m = Manager(connection)
    except (ConnectionError, MaxRetryError, NewConnectionError):
        print("Error with connection. Probably you don't have internet connection")
    else:
        try:
            main()
        finally:
            m.finish_work()
else:
    print("I won't work like that. You have to start the app directly from it's main file")