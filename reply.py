#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import queue
from typing import Optional
from threading import Thread
from lib.traffic import TrafficLoad, TrafficData


class ReplyProxy:
    def __init__(self, data: TrafficData):
        self.data: TrafficData = data
        self.index = 0

        self.connected = True

        self.in_queue = queue.Queue()
        self.in_thread: Optional[Thread] = None
        self.in_socket: Optional[socket.socket] = None

        self.out_queue = queue.Queue()
        self.out_thread: Optional[Thread] = None

    def start(self, conn: socket.socket):
        self.in_thread = Thread(target=self.start_queue_incoming, args=(conn, ))
        self.in_thread.start()

        self.out_thread = Thread(target=self.start_queue_outgoing)
        self.out_thread.start()

        self.try_send()

    def start_queue_outgoing(self):
        print('ReplyProxy.start_queue_outgoing->start')
        while self.connected:
            outgoing = self.out_queue.get()
            print('ReplyProxy.start_queue_outgoing', outgoing)
            self.index += 1
            self.try_send()
        print('ReplyProxy.start_queue_outgoing->stop')

    def try_send(self):
        if not self.connected:
            return
        print('ReplyProxy.try_send->start', self.index)
        while self.data.packets[self.index].has_input:
            packets = self.data.packets[self.index]
            for packet in packets.input:
                self.in_queue.put(packet)
            self.index += 1
        print('ReplyProxy.try_send->end', self.index)

    def start_queue_incoming(self, s: socket.socket):
        print('ReplyProxy.start_client_incoming->start')
        self.in_socket = s
        while self.connected:
            incoming = self.in_queue.get()
            print('ReplyProxy.start_client_incoming', self.index)
            s.sendall(incoming)
        print('ReplyProxy.start_client_incoming->stop')


def start_server(tfdata: TrafficData, host='127.0.0.1', port=3307):
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
                    p: ReplyProxy = ReplyProxy(tfdata)
                    p.start(conn)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        print('start_server->data', data)
                        p.out_queue.put(data)
                    print(f'Connection closed from {addr}')
                    print('Replayed packets', p.index, 'of', len(p.data.packets))
        finally:
            print('stop_server', host, port)
            s.close()


if __name__ == '__main__':
    tfdata = TrafficLoad.load_packets()
    start_server(tfdata=tfdata)
