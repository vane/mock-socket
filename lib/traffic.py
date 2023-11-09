#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import pickle
from typing import Optional

version = b'ver:0.0.1:'


class TrafficPacket:
    def __init__(self):
        self.has_input = False
        self.has_output = False
        self.input = []
        self.output = []


class TrafficData:

    def __init__(self):
        self.current_packet: Optional[TrafficPacket] = None
        self.packets: list[TrafficPacket] = []

    def in_packet(self, input):
        print('TrafficData.in_packet')
        if self.current_packet and self.current_packet.has_output:
            self.packets.append(self.current_packet)
            print('in_packet->end')
        self.current_packet = TrafficPacket()
        self.current_packet.input.append(input)
        self.current_packet.has_input = True
        pass

    def out_packet(self, output):
        print('TrafficData.out_packet')
        if self.current_packet and self.current_packet.has_input:
            self.packets.append(self.current_packet)
            print('out_packet->end')
        self.current_packet = TrafficPacket()
        self.current_packet.input.append(output)
        self.current_packet.has_output = True


class TrafficDump:
    @staticmethod
    def dump_packets(packets: list[TrafficPacket], fname='dump.bin'):
        print('TrafficDump.dump->start')
        with open(fname, 'wb+') as f:
            f.write(version)
            for packet in packets:
                b = io.BytesIO()
                pickle.dump(packet, b)
                size = f'{b.getbuffer().nbytes:010d}'
                f.write(size.encode('utf-8'))
                print('TrafficDump.dump', size)
                b.seek(0)
                f.write(b.read())
        print('TrafficDump.dump->end')


class TrafficLoad:
    @staticmethod
    def load_packets(fname='dump.bin') -> TrafficData:
        print('TrafficLoad.load_packets->start')
        tf: TrafficData = TrafficData()
        with open(fname, 'rb') as f:
            f.read(len(version))
            val = f.read(10)
            while val:
                b = io.BytesIO()
                data = f.read(int(val))
                b.write(data)
                b.seek(0)
                packet = pickle.load(b)
                print(val, packet)
                val = f.read(10)
                tf.packets.append(packet)
        print('TrafficLoad.load_packets->end')
        return tf
