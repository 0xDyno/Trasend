import os
import pickle
from tools import *


class Wallet:

    def get_all_info(self):
        return f"{self.label} : {self.address} : {self.mnemonic} : {self.private_key}"

    def get_as_string(self, sep=dev):
        # возвращает строку для сохранения
        l = self.label.strip()              # чистит от пробелов и табов
        a = self.address.strip()
        m = self.mnemonic.strip()
        p =  self.private_key.strip()
        return l + sep + a + sep + m + sep + p

    def __init__(self, address, label="None", mnemonic="None", private_key="None"):
        self.label = label
        self.address = address
        self.mnemonic = mnemonic
        self.private_key = private_key

    def __str__(self):
        if self.label != "None":
            return f"{self.label}: {self.address}"
        else:
            return f"Address {self.address}"

    def __repr__(self):
        return self.__str__()


def check_and_create_dirs():
    if not os.path.exists("saved/"):
        os.mkdir("saved/")
    if not os.path.exists("saved/reserve/"):
        os.mkdir("saved/reserve/")


def save_list_of_addresses(list_of_addresses: list):
    """Gives list of objects and save it in binary
    Can't be read human, no backup"""
    check_and_create_dirs()             # Проверка на существования пути
    with open(save, "wb") as w:         # Сохраняем в файл
        for el in list_of_addresses:
            w.write(pickle.dumps(el))
            w.write(dev.encode())


def get_list_of_addresses():
    """Open a file and recover objects"""
    list_of_addresses = list()

    # Считываем байты из файла, разделяем и добавляем в лист
    with open(save, "rb") as r:
        get_bytes = r.read()
        list_of_bytes = get_bytes.split(dev.encode())

    # Проходимся по каждому елементы и трансформируем в объект
    for el in list_of_bytes:

        if not el:
            continue             # проверка на пустую строку

        address = pickle.loads(el)
        list_of_addresses.append(address)

    return list_of_addresses


def save_list_of_addresses_old(list_of_addresses: list):
    """
    Gives list with Wallet objects and save it in the file.
    No encrypt, data is readable
    :param list_of_addresses: list with Wallet objects (addresses)
    :return: None
    """
    # If there are no folders - it will create them
    check_and_create_dirs()

    # Сохраняем в файл
    with open(save_old, "w") as w:
        for address in list_of_addresses:
            w.write(address.get_as_string() + "\n")

    # Сохраняем в резервный файл без перезаписи
    with open(save_reserve, "a") as w:
        w.write("\n --==-- \n")                 # Отступ
        for address in list_of_addresses:
            w.write(address.get_as_string() + "\n")
        w.write("\n --==-- \n")                 # Отступ


def get_list_of_addresses_old():
    """
    Takes data from the file, transforms it as an object and add to the list
    Data should be in UTF-8 format as strings
    :return: List of Wallet objects
    """
    list_of_addresses: list = list()

    # Читаем содержимое файла, разделяем по ентеру и сохраняем лист в переменную
    with open(save_old, "r") as r:
        lines = r.read().split("\n")

    # Обрабатываем каждую строку и добавляем в лист
    for line in lines:
        list_of_value = line.split(dev)                 # разделяем строку по разделителю

        if not line:                                    # проверка на пустую строку
            continue

        address = Wallet(label=list_of_value[0],        # создаем объект данными
                         address=list_of_value[1],
                         mnemonic=list_of_value[2],
                         private_key=list_of_value[3])
        list_of_addresses.append(address)               # добавляем объект в лист

    return list_of_addresses
