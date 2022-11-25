DEFAULT_DIVIDER = " "
DEFAULT_NETWORK = "ETH"
ETH_ADDR_LENGTH = 42
ETH_KEY_LENGTH = 66


def string_to_dict(ask_divider=True, network=DEFAULT_NETWORK):
    # Если своей разделитель - спросит его по дефолту
    if ask_divider:
        divider = ask_for_divider()
    else:
        divider = DEFAULT_DIVIDER

    dict_with_addresses = dict()

    print("Insert the data:")
    while True:
        line = input()                                  # считывание строки
        if line:                                        # если не пустая
            if line.__contains__("exit"):               # проверить на выход
                break
            line = line.split(divider)                  # разделить по разделителю


            # Проверить на соответствие формата к сети.
            if check_conditions(line, network):
                dict_with_addresses[line[0]] = line[1]
            else:
                print(f"====>>>> Произошла ошибка, это не похоже на правильный кошелек. Проверьте данные.\n"
                      f"====>>>> Должно быть 42 символа в адресе и 66 в приватнике{line}\n"
                      f"====>>>> Эта инфа сохранена не была")
        else:
            break
    return dict_with_addresses


def ask_for_divider():
    divider = input(f"Введите разделитель (либо enter для дефолтного \"{DEFAULT_DIVIDER}\"): ")

    if not divider:  # Если пустая - поставит пробел
        divider = DEFAULT_DIVIDER

    return divider


def check_conditions(line, network):
    if not network:
        return True

    match network:
        case "ETH":
            return len(line[0]) == 42 and \
                   line[0].startswith("0x") and \
                   len(line[1]) == 66 and \
                   line[1].startswith("0x")
        case _:
            return True


def print_the_dict(dict_with_addresses: dict):
    if not dict_with_addresses:
        return f"The list is empty:\n{dict_with_addresses}"

    for k, v in dict_with_addresses.items():
        print(f"\"{k}\": \"{v}\"", end=",\n")


def main(ask_divider):
    dict_with_addresses: dict = string_to_dict(ask_divider)
    print_the_dict(dict_with_addresses)


if __name__ == "__main__":
    main(ask_divider=False)
