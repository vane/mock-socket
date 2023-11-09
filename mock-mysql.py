#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import struct
MAX_PACKET_LEN = 2**24 - 1

class ConnectionModel:
    def __init__(self, connection):
        self._conn = connection
        self._packet_number = 0

    @property
    def packet_number(self):
        return self._packet_number

    @property
    def connection(self):
        return self._conn

    def next_packet(self):
        self._packet_number = (self._packet_number + 1) % 256


def write_server_information(model: ConnectionModel):
    btrl = 4
    btrh = 4
    bytes_to_write = btrl + (btrh << 16)
    data = struct.pack('<HBB', btrl, btrh, model.packet_number)
    print('write_server_information', bytes_to_write, len(data))
    model.connection.send(data)


def start_server(host='127.0.0.1', port=3306):
    print(f'Server started {host}:{port}')
    models = {}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            model = ConnectionModel(connection=conn)
            write_server_information(model=model)
            with conn:
                print(f'Connection new from {addr}')
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print('data', data)
            print(f'Connection closed from {addr}')
    pass


if __name__ == '__main__':
    print('ok')
    start_server()