import socket

class Connector:
    def __init__(self, host: str):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (host, 5051)
        self.sock.connect(self.addr)

    def send_message(self, message: str):
        self.sock.sendall(message.encode())
        try:
            resp = self.sock.recv(1488)
        except Exception:   
            return
    
        return resp.strip(b"\x00")

    def close_connection(self):
        self.sock.close()