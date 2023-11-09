#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import queue
from typing import Optional
from threading import Thread
from lib.traffic import TrafficData, TrafficDump


class Proxy:
    def __init__(self):
        self.connected = True
        self.in_queue = queue.Queue()
        self.in_thread: Optional[Thread] = None
        self.in_socket: Optional[socket.socket] = None

        self.out_queue = queue.Queue()
        self.out_thread: Optional[Thread] = None
        self.out_socket: Optional[socket.socket] = None

        self.data = TrafficData()

    def outgoing_client_socket(self, host='127.0.0.1', port=3306):
        print('Proxy.start_client->start')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            self.out_thread = Thread(target=self.start_queue_outgoing, args=(s, ))
            self.out_thread.start()
            while self.connected:
                try:
                    data = s.recv(1024)
                    if not data:
                        break
                    print('Proxy.outgoing_client_socket->data', data)
                    self.in_queue.put(data)
                    self.data.in_packet(data)
                except:
                    print('Proxy.outgoing_client_socket->error')
                    self.connected = False
                    break
        print('Proxy.start_client_socket->end')

    def start_queue_outgoing(self, s: socket.socket):
        print('Proxy.start_queue_outgoing->start')
        self.out_socket = s
        while self.connected:
            outgoing = self.out_queue.get()
            print('Proxy.start_queue_outgoing', outgoing)
            if self.connected:
                s.sendall(outgoing)
        print('Proxy.start_queue_outgoing->stop')

    def start_queue_incoming(self, s: socket.socket):
        print('Proxy.start_client_incoming->start')
        self.in_socket = s
        while self.connected:
            incoming = self.in_queue.get()
            print('Proxy.start_client_incoming', incoming)
            s.sendall(incoming)
        print('Proxy.start_client_incoming->stop')

    def start(self, conn: socket.socket):
        self.out_thread = Thread(target=self.outgoing_client_socket)
        self.out_thread.start()
        self.in_thread = Thread(target=self.start_queue_incoming, args=(conn, ))
        self.in_thread.start()

    def disconnect_outgoing(self):
        print('Proxy.disconnect_outgoing')
        self.connected = False
        self.in_socket.close()

    def disconnect_incoming(self):
        print('Proxy.disconnect_incoming')
        self.connected = False
        self.out_socket.close()


def start_server(host='127.0.0.1', port=3307):
    print('start_server', host, port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
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
                        p.data.out_packet(data)
                        p.out_queue.put(data)
                    p.disconnect_incoming()
                    print(f'Connection closed from {addr}')
                    print('Recorded packets', len(p.data.packets))
                    TrafficDump.dump_packets(packets=p.data.packets)
        finally:
            print('stop_server', host, port)
            s.close()


if __name__ == '__main__':
    print('ok')
    start_server()
