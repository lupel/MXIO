#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket

from main.configuration import Configuration
from main.slave import Slave

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
        def close_socket(s: socket.socket, return_code=None):
            try:
                if return_code:
                    s.send(return_code)
                s.close()
            except:
                pass
            #
        self.socket.listen(5)
        while True:
            try:
                (client, address) = self.socket.accept()
                logging.debug(f'Server: request from {str(address)}')
                slave_address = client.recv(40)
                if not slave_address or slave_address == b'':
                    logging.warning(f'Server: slave_address empty: {slave_address}')
                    close_socket(client, return_code=b'\0')
                    continue
                slave_address = int(slave_address[0])
                if slave_address == 0 or slave_address > len(self.slaves):
                    logging.warning(f'Server: slave_address out of range: {slave_address}')
                    close_socket(client, return_code=b'\0')
                    continue
                # slave address is in limits - trying to receive parcel
                response = self.slaves[slave_address - 1].receive(
                    slave_address=slave_address,
                    client=client
                )
                if not response:
                    close_socket(client, b'\0')
                else:
                    close_socket(client, response)
            except Exception as e:
                logging.error(f'Server: {str(e)}')
            finally:
                close_socket(client)
        pass
