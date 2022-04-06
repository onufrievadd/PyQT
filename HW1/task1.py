"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""


from subprocess import Popen, PIPE
from ipaddress import ip_address
from tabulate import tabulate
import socket



def host_ping(addresses_list, timeout, count):
    res = {'Доступные узлы': [], 'Недоступные узлы': []}
    for address in addresses_list:
        try:
            address = ip_address(address)
        except ValueError:
            try:
                address = socket.gethostbyname(address)
            except Exception:
                print(f'Bad address - {address}')
                continue
        operation = Popen(['ping', f'-W {timeout}', f'-c {count}', f'{address}'], shell=False, stdout=PIPE)
        operation.wait()
        if operation.returncode == 0:
            print(f'Узел {address} доступен')
        else:
            print(f'Узел {address} недоступен')
    return res


if __name__ == '__main__':
    list_of_addresses = ['192.168.8.1', '8.8.8.8', 'yandex.ru', 'google.com',
                         '0.0.0.1', '0.0.0.2', '0.0.0.3', '0.0.0.4', '0.0.0.5',
                          '0.0.0.6', '0.0.0.7', '0.0.0.8', '0.0.0.9', '0.0.1.0']
    host_ping(list_of_addresses, 500, 1)
