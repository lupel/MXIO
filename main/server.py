#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket

from main.configuration import Configuration


class Server:
    def __init__(self, slaves):
        if not len(slaves):
            raise Exception('Server: no slaves passed')
        self.slaves = slaves
        self.config = Configuration().server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', self.config.port))
        logging.info(f'Server: listen 0.0.0.0:{self.config.port}')

    def spawn(self):
        def answer_to_client(s: socket.socket, response=None, disconnect=False):
            try:
                if response:
                    logging.debug(f'Server: response: {response.hex()}')
                    s.sendall(response)
                if disconnect:
                    s.close()
            except:
                pass
            #
        self.socket.listen(1)
        (client, address) = (None, None)
        while True:
            try:
                if not client:
                    (client, address) = self.socket.accept()
                logging.debug(f'Server: request from {str(address)}')
                data = client.recv(12228)
                logging.debug(f'Server: received: {data.hex()}')
                if not data or data == b'' or data == b'\0':
                    logging.error(f'Server: no data was received: {slave_address}')
                    answer_to_client(client, disconnect=True)
                    client = None
                    continue
                elif len(data) < 8:
                    logging.error(f'Server: data length < 8: {len(data)}')
                    answer_to_client(client, disconnect=True)
                    client = None
                    continue
                slave_address = int(data[6])
                if slave_address == 0 or slave_address > len(self.slaves) or not slave_address:
                    logging.error(f'Server: slave_address out of range: {slave_address}')
                    answer_to_client(client, disconnect=True)
                    client = None
                    continue
                # slave address is in limits - trying to receive parcel
                response = self.slaves[slave_address - 1].receive(
                    slave_address=slave_address,
                    data=data
                )
                if not response:
                    answer_to_client(client, disconnect=True)
                    client = None
                else:
                    answer_to_client(client, response)
            except Exception as e:
                logging.error(f'Server: {str(e)}')
                answer_to_client(client, disconnect=True)
                client = None
        pass
