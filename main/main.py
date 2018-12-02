#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from time import sleep
from os import getenv

from main.configuration import Configuration
from main.url import Url


class Entrypoint:
    def __init__(self):
        self.logging_configuration()
        self.config = Configuration()
        # empty arrays with urls and stat about quantity of fails
        self.urls = [Url(u, curl_enabled=True) for u in self.config.curl.urls]
        for u in self.config.ping.urls:
            # this loop for avoiding of duplicates
            existent_object = [o for o in self.urls if o.url == u]
            if existent_object:
                existent_object[0].ping_enabled = True
            else:
                self.urls.append(Url(u, ping_enabled=True))

    def logging_configuration(self):
        logging_format = '%(asctime)s [%(levelname)s] Line: %(lineno)d | %(message)s'
        if getenv('DEBUG', 'false').lower() == 'true':
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO
        logging.basicConfig(format=logging_format, level=logging_level)

    def main(self):
        while True:
            for u in self.urls:
                u.check()
            sleep(self.config.checking.interval)
        pass


def entrypoint():
    Entrypoint().main()


if __name__ == '__main__':
    entrypoint()
