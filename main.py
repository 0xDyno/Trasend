from web3 import Web3
from requests import ConnectTimeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

import user_settings
from config import texts
from config.settings import version
from src.manager import Manager


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
                case "01":                            # check connection
                    m.connection_status()
                case "02":                            # last block info
                    m.print_gas_price_info()
                case "03":                            # change connection
                    m.set_new_connection()
                case "upd":                           # update wallets
                    m.update_wallets()
                case "label":                         # change label
                    m.change_label()
                case "v":
                    print(f"Version {version}")
                case "exit":
                    break
                case "e":
                    break
                case "h":
                    print("\n%s\n---------------------" % texts.instruction_main)
                case _:
                    print(texts.wrong_command_main)
        except (AssertionError, TypeError, IndexError,
                ValueError, InterruptedError, PermissionError) as e:
            print(e)
        except (ConnectionError, MaxRetryError, NewConnectionError, ConnectTimeout):
            print("\n> Error with connection. Probably you don't have internet connection.")
        except KeyboardInterrupt:
            print("\n> Finished")
            break
            
            
def connect():
    count = 1
    rpc = user_settings.RPC_Point
    
    while count < 6:
        print(texts.trying_connect, end=" ")
        connection = Web3(Web3.HTTPProvider(rpc))
        
        if connection.isConnected():
            print(texts.success)
            manager = Manager(connection)
            return manager
        else:
            print(f"Attempt #{count} - Failed \n"
                  "> RPC point doesn't work. Change new RPC in user_settings.py or write here")
            new_rpc = input("> ").strip()
            rpc = new_rpc if new_rpc else rpc
        count += 1
    else:
        raise InterruptedError("> Wasn't able to connect to the network. Try again later.")


if __name__ == "__main__":
    try:
        m = connect()
    except Exception as ee:
        print(ee)
    else:
        try:
            main()
        finally:
            m.finish_work()
else:
    print("> You have to start the app directly")