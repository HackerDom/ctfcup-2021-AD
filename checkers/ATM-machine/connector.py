import socket

class Connector:
    def __init__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = address
        self.sock.connect(self.addr)

    def send_message(self, message):
        self.sock.sendall(message)
        try:
            resp = self.sock.recv(1488)
        except Exception:
            return
        print(len(resp))
        return resp.strip(b"\x00")

    def close_connection(self):
        self.sock.close()
