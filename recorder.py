#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import queue
from typing import Optional
from threading import Thread


class Proxy:
    connected = True
    incoming = queue.Queue()
    outgoting = queue.Queue()

    def __init__(self):
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()
        self.in_thread: Optional[Thread] = None
        self.out_thread: Optional[Thread] = None

    def start_client(self, host='127.0.0.1', port=3306):
        print('start_client')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            othread = Thread(target=self.start_client_outgoing, args=(s, ))
            othread.start()
            while Proxy.connected:
                data = s.recv(1024)
                if not data:
                    break
                print('start_client->data', data)
                Proxy.incoming.put(data)


    def start_client_outgoing(self, s: socket.socket):
        while Proxy.connected:
            outgoing = Proxy.outgoting.get()
            print('start_client_outgoing', outgoing)
            s.sendall(outgoing)


    def start_client_incoming(self, s: socket.socket):
        while Proxy.connected:
            incoming = Proxy.incoming.get()
            print('start_client_incoming', incoming)
            s.sendall(incoming)

    def start(self, conn: socket.socket):
        self.out_thread = Thread(target=self.start_client)
        self.out_thread.start()
        self.in_thread = Thread(target=self.start_client_incoming, args=(conn, ))
        self.in_thread.start()

    def dispose(self):
        self.in_thread.join()
        self.out_thread.join()


def start_server(host='127.0.0.1', port=3307):
    print('start_server', host, port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print(f'Connection new from {addr}')
                p = Proxy()
                p.start(conn)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print('start_server->data', data)
                    Proxy.outgoting.put_nowait(data)

                Proxy.connected = False
                print(f'Connection closed from {addr}')


if __name__ == '__main__':
    print('ok')
    start_server()
