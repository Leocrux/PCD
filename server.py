import socket
import argparse


class GenericServer:
    def __init__(self, protocol, ip, port, buffer_size=4096, ack=False):
        self._protocol = protocol.lower()
        self._socket = self._get_socket(protocol, ip, port)
        self.buffer_size = buffer_size
        self.received_bytes = 0
        self.received_messages = 0
        self._ack = ack

    @staticmethod
    def _get_socket(protocol, ip, port):
        sock = None
        if protocol.lower() == 'tcp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if protocol.lower() == 'udp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if sock:
            sock.bind((ip, port))
        return sock

    def receive_data(self):
        if self._protocol == 'tcp':
            print('Listening')
            self._socket.listen(1)
            conn, addr = self._socket.accept()
            print("Connected {}".format(addr))
        else:
            print("Waiting message")
            conn = self._socket
        while True:
            data = None
            address = None
            if self._protocol == "tcp":
                data = conn.recv(self.buffer_size)
            elif self._protocol == 'udp':
                data, address = conn.recvfrom(self.buffer_size)
            if self._ack:
                if self._protocol == "tcp":
                    conn.send(b'ack')
                elif self._protocol == 'udp':
                    conn.sendto(b'ack', address)
            if not data:
                break
            self.received_bytes += len(data)
            self.received_messages += 1
            if b'exit' in data:
                break

        msg = "Protocol {}\n".format(self._protocol)
        msg += "Ack {}\n".format(self._ack)
        msg += "Buffer_size {}\n".format(self.buffer_size)
        msg += "Received {} bytes\n".format(self.received_bytes)
        msg += "Received {} messages\n".format(self.received_messages)
        return msg


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--protocol", default="TCP", help="Select UDP/TCP. default TCP", choices=['TCP', "UDP"])
    parser.add_argument("-b", "--buffer", default=1024, type=int,
                        help="Buffer size. Default 1024. Select int from 1 to 65535")
    parser.add_argument("-P", "--Port", default=4949, type=int,
                        help="Port to use. default 4949, select from 1024 49151")
    parser.add_argument("-A", "--ack", default=False, action='store_true',
                        help="Select if server needs to send ack back to client Default is False")
    parser.add_argument("-L", "--log")
    args = parser.parse_args()

    server = GenericServer(args.protocol, 'localhost', args.Port, buffer_size=args.buffer, ack=args.ack)
    msg = server.receive_data()
    with open(args.log, 'w') as f:
        f.write(msg)
