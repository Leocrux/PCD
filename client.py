import socket
import argparse
import time

KB = 1024
MB = 1024 * KB


class GenericClient:
    def __init__(self, protocol, ip, port, data_size=MB, buffer_size=4096, ack=False):
        self._protocol = protocol.lower()
        self._socket = self._get_socket(protocol, ip, port)
        if buffer_size > data_size:
            buffer_size = data_size
        self.buffer_size = buffer_size
        self.sent_bytes = 0
        self.data_size = data_size
        self.sent_messages = 0
        self._ack = ack

    @staticmethod
    def _get_socket(protocol, ip, port):
        sock = None
        if protocol.lower() == 'tcp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if protocol.lower() == 'udp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if sock:
            print("Connecting to {}:{}".format(ip, port))
            sock.connect((ip, port))
        return sock

    def stream_data(self):
        start = time.time()
        while self.sent_bytes < self.data_size:
            self.sent_bytes += self._socket.send(b'a' * self.buffer_size)
            if self._ack:
                ack = self._socket.recv(1024)
            self.sent_messages += 1

        if self._protocol == 'udp':
            self._socket.send(b'exit')
            self.sent_bytes += 4
            self.sent_messages += 1

        finish = time.time()
        time_spent = finish - start

        msg = "Protocol {}\n".format(self._protocol)
        msg += "Ack {}\n".format(self._ack)
        msg += "Buffer_size {}\n".format(self.buffer_size)
        msg += "Sent {} bytes\n".format(self.sent_bytes)
        msg += "Sent {} messages\n".format(self.sent_messages)
        msg += "Transmission time was {} seconds\n".format(time_spent)
        return msg


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--protocol", default="TCP", help="Select UDP/TCP. default TCP", choices=['TCP', "UDP"])
    parser.add_argument("-b", "--buffer", default=1024, type=int,
                        help="Buffer size. Default 1024. Select int from 1 to 65535")
    parser.add_argument("-P", "--Port", default=4949, type=int,
                        help="Port to use. default 4949, select from 1024 to 49151")
    parser.add_argument("-I", "--ip", default="localhost", type=str, help="Ip to connect to. default localhost")
    parser.add_argument("-S", "--size", default=MB, type=int,
                        help="Size of data to send in bytes. Default 1MB")
    parser.add_argument("-A", "--ack", default=False, action='store_true',
                        help="Select if client needs to wait for ack before sending another message. Default is False")
    parser.add_argument("-L", "--log")

    args = parser.parse_args()

    server = GenericClient(args.protocol, args.ip, args.Port, data_size=args.size, buffer_size=args.buffer,
                           ack=args.ack)

    msg = server.stream_data()
    with open(args.log, 'w') as f:
        f.write(msg)
