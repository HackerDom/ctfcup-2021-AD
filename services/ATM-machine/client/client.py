import socket

from enum import IntEnum
from typing import Dict, List
from base64 import b64decode, b64encode


UTF_8 = 'utf-8'


class Stage(IntEnum):
    START = 1
    TRANSFER = 2
    CHECKID = 3
    CHECK = 4
    SHOW = 5
    SEND = 6


class BaseMsg:
    def get_bytes(self) -> bytes:
        return str(self).encode()


class Transfer(BaseMsg):
    def __init__(self):
        self.to: str = ''
        self.from_: str = ''
        self.value: float = -1
        self.comment: str = ''

    def __str__(self) -> str:
        return f'transfer {self.to} {self.from_} {self.value} {self.comment}'


class CheckId(BaseMsg):
    def __init__(self):
        self.id: int = -1

    def __str__(self) -> str:
        return f'checkid {self.id}'


class Check(BaseMsg):
    def __init__(self):
        self.encrypt_bytes: bytes = b''

    def __str__(self) -> str:
        return f'check {self.encrypt_bytes}'

    def get_bytes(self) -> bytes:
        return 'check '.encode() + self.encrypt_bytes


class Show(BaseMsg):
    def __init__(self):
        self.offset: int = -1
        self.limit: int = -1

    def __str__(self) -> str:
        return f'show {self.offset} {self.limit}'


class Sender:

    def __init__(self, stage: Stage, msg: BaseMsg):
        self.prev_stage: Stage = stage
        self.msg: BaseMsg = msg
        self.host = '0.0.0.0'
        self.port = 5051

    @staticmethod
    def print_transfer_answer(data: bytes):
        split_data = data.strip(b'\x00').split(b'\n')
        print(f'id: {split_data[0].decode(UTF_8)}  {b64encode(split_data[1]).decode(UTF_8)}')

    @staticmethod
    def print_check_id_answer(data: bytes):
        print(data.strip(b'\x00').decode(UTF_8))

    @staticmethod
    def print_check_answer(data: bytes):
        print(data.strip(b'\x00').decode(UTF_8))

    @staticmethod
    def print_show_answer(data: bytes):
        split_data = data.strip(b'\x00').split('separator'.encode())
        print('encrypted transactions:')
        for el in split_data:
            print(b64encode(el).decode(UTF_8))

    def handle_message(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(self.msg.get_bytes())
            data: bytes = sock.recv(1488)
            if self.prev_stage == Stage.TRANSFER:
                self.print_transfer_answer(data)
            elif self.prev_stage == Stage.CHECKID:
                self.print_check_id_answer(data)
            elif self.prev_stage == Stage.CHECK:
                self.print_check_answer(data)
            elif self.prev_stage == Stage.SHOW:
                self.print_show_answer(data)


class MachineGun:
    START_COMMANDS: List[str] = ['transfer', 'checkid', 'check', 'show']
    STRING_TO_STAGE: Dict[str, Stage] = {
        'transfer': Stage.TRANSFER,
        'checkid': Stage.CHECKID,
        'check': Stage.CHECK,
        'show': Stage.SHOW
    }

    def __init__(self):
        self.stage: Stage = Stage.START
        self.prev_stage: Stage = Stage.START
        self.msg = None

    @staticmethod
    def _validate_string(input_msg: str) -> str:
        res = input(input_msg)
        while res == '':
            res = input(input_msg)
        return res

    @staticmethod
    def _validate_num(input_msg: str, num_type: type):
        value = -1
        while value <= 0:
            try:
                value = num_type(input(input_msg))
            except ValueError:
                print('enter the number > 0')
                value = -1
        return value

    @staticmethod
    def _validate_bytes(input_msg: str) -> bytes:
        res = input(input_msg)
        while res == '':
            res = input(input_msg)
        return b64decode(res)

    def handle_start(self):
        possible_commands = "; ".join(self.START_COMMANDS)
        command = input(f'possible commands: {possible_commands}\n')
        while command not in self.START_COMMANDS:
            command = input(f'possible commands: {possible_commands}\n')
        self.prev_stage = self.stage
        self.stage = self.STRING_TO_STAGE[command]

    def handle_transfer(self):
        transfer = Transfer()
        transfer.to = self._validate_string('to:\n')
        transfer.from_ = self._validate_string('from:\n')
        transfer.value = self._validate_num('value:\n', float)
        transfer.comment = self._validate_string('comment:\n')
        self.prev_stage = self.stage
        self.stage = Stage.SEND
        self.msg = transfer

    def handle_check_id(self):
        check_id = CheckId()
        check_id.id = self._validate_num('id:\n', int)
        self.prev_stage = self.stage
        self.stage = Stage.SEND
        self.msg = check_id

    def handle_check(self):
        check = Check()
        check.encrypt_bytes = self._validate_bytes('encrypt bytes in base64:\n')
        self.prev_stage = self.stage
        self.stage = Stage.SEND
        self.msg = check

    def handle_show(self):
        show = Show()
        show.offset = self._validate_num('offset:\n', int)
        show.limit = self._validate_num('limit:\n', int)
        self.prev_stage = self.stage
        self.stage = Stage.SEND
        self.msg = show

    def run(self):
        while True:
            try:
                if self.stage == Stage.START:
                    self.handle_start()
                elif self.stage == Stage.TRANSFER:
                    self.handle_transfer()
                elif self.stage == Stage.CHECKID:
                    self.handle_check_id()
                elif self.stage == Stage.CHECK:
                    self.handle_check()
                elif self.stage == Stage.SHOW:
                    self.handle_show()
                elif self.stage == Stage.SEND:
                    sender = Sender(self.prev_stage, self.msg)
                    sender.handle_message()
                    self.stage = Stage.START
                    self.prev_stage = Stage.START
            except Exception:
                print('kernel panic')
                self.stage = Stage.START


def main():
    try:
        gun = MachineGun()
        gun.run()
    except KeyboardInterrupt:
        exit(0)


if __name__ == '__main__':
    main()


# thread_pool = ThreadPool(processes=7)
#
#
# def main():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     addr = ('0.0.0.0', 5051)
#     sock.connect(addr)
#     sock.sendall('transfer a v 100 '.encode() + ('a'*3).encode())  # 'transfer <from> <to> <value> <comment>'
#     answ = sock.recv(1488).strip(b'\x00').split(b'\n')  # разделитель \n
#     _id = int(answ[0].decode('utf-8'))  # id транзакции
#     print(_id)
#     print(answ[1])  # [int(x) for x in answ[1]]
#     sock.sendall('checkid '.encode() + str(_id).encode())  # 'checkid <id>'
#     print(sock.recv(1488).strip(b'\x00').decode('utf-8'))  # тело транзакции или not found
#     sock.sendall('show 0 1'.encode())  # 'show'
#     transactions = sock.recv(1488).strip(b'\x00').split(b'\n')  # список транзакций
#     print(answ[1] in transactions)  # проверка сеществования транзакции в бд
#     sock.sendall('check '.encode() + transactions[0][:-1] + b'x\23')  # 'check <шифротекст>'
#     print(sock.recv(1488).strip(b'\x00').decode('utf-8'))  # ok или error
#     sock.close()
    # for _ in range(100):
    #     thread_pool.apply_async(main)
    # thread_pool.close()
    # thread_pool.join()
