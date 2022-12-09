from manager import Manager
from config.text import main_text_instruction
from web3 import Web3
import config.keys


def main():
    print("\n%s\n---------------------" % main_text_instruction)
    while True:
        text = input().lower()
        match text:
            case "1":
                m.print_wallets()
            case "2":
                m.try_add_wallet()
            case "3":
                number = input("How many wallets generate? (up to 100) >>> ")
                if number.isnumeric():
                    m.generate_wallets(int(number))
                else:
                    print("Not a number")
            case "4":
                m.try_delete_wallet()
            case "5":
                print(f"Connection status: {m.web3.isConnected()}")
            case "6":
                m.update_wallets()
            case "7":
                m.print_block_info()
            case "8":   # Send Transaction
                """
                ну да, не самое простое... 
                Нужно решить куда захламлять код - если в менеджен - он будет дохера большой
                Если делать отдельный файл - то это будут функции, либо классы... классы тоже Ок
                Чисто функциональные
                
                А то менеджер дофига большой, и это факт. Всё что возможно - лучше вынести в помощника:
                print wallets - и пусть у себя будет, вызывает метод с помощника
                print_block_info - с передачей менеджера
                А транзы - в свой файл. 
                
                """
                pass
            case "9":   # ??
                pass
            case "t":
                pass
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
    except Exception as e:
        print(e)
    finally:
        m.finish_work()
else:
    print("I won't work like that. You have to start the app directly from it's main file")