import socket
import time
import random

from multiprocessing.pool import ThreadPool


thread_pool = ThreadPool(processes=7)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ('0.0.0.0', 5051)
    sock.connect(addr)
    sock.sendall('transfer a v 100 '.encode() + ('a'*30).encode())  # 'transfer <from> <to> <value> <comment>'
    answ = sock.recv(1488).strip(b'\x00').split(b'\n')  # разделитель \n
    _id = int(answ[0].decode('utf-8'))  # id транзакции
    print(_id)
    print(answ[1])  # [int(x) for x in answ[1]]
    sock.sendall('checkid '.encode() + str(_id).encode())  # 'checkid <id>'
    print(sock.recv(1488).strip(b'\x00').decode('utf-8'))  # тело транзакции или not found
    sock.sendall('show 0 1'.encode())  # 'show'
    transactions = sock.recv(1488).strip(b'\x00').split(b'\n')  # список транзакций
    print(answ[1] in transactions)  # проверка сеществования транзакции в бд
    sock.sendall('check '.encode() + transactions[0])  # 'check <шифротекст>'
    print(sock.recv(1488).strip(b'\x00').decode('utf-8'))  # ok или error
    sock.close()


if __name__ == '__main__':
    main()
    # for _ in range(100):
    #     thread_pool.apply_async(main)
    # thread_pool.close()
    # thread_pool.join()
