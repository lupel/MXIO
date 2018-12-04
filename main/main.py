#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from main.configuration import Configuration
from main.server import Server
from main.slave import Slave

class Entrypoint:
    def __init__(self):
        self.config = Configuration()

    def main(self):
        try:
            slaves = []
            for i in range(self.config.slave.quantity):
                slaves.append(Slave(address=bytes([i+1])))
            Server(slaves=slaves).spawn()
        except Exception as e:
            logging.error(f'Entrypoint: {str(e)}')
        pass


def entrypoint():
    Entrypoint().main()


if __name__ == '__main__':
    entrypoint()
