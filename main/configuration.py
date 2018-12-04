#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Read about environment variables in README.md

import logging
import yaml

from os import getenv, path


class Configuration(object):
    singleton_object = None

    @staticmethod
    def configure_logging():
        """
        Configure logging depending on server settings.
        :return:
        """
        logging_format = '%(asctime)s [%(levelname)s] Line: %(lineno)d | %(message)s'
        if getenv('DEBUG', 'false').lower() == 'true':
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO
        logging.basicConfig(format=logging_format, level=logging_level)

    def __new__(cls, *args, **kwargs):
        if not Configuration.singleton_object:
            Configuration.configure_logging()
            logging.debug('Config: creating new object')
            Configuration.singleton_object = super().__new__(cls, *args, **kwargs)
        return Configuration.singleton_object

    class GeneralConfiguration:
        def __init__(self, debug=None):
            self.debug = debug

    class ServerConfiguration:
        def __init__(self, port=None):
            self.port = port

    class SlaveConfiguration:
        def __init__(self, quantity=None):
            self.quantity = quantity
            pass

    def _read_config_file(self):
        conf_path = getenv('CONFIG_PATH', '/app/config.yaml')
        if path.exists(conf_path):
            with open(conf_path, 'r') as file:
                try:
                    self.config = yaml.load(file)
                    logging.debug(self.config)
                except yaml.YAMLError as e:
                    logging.error(f'Config: YAML parse error: {str(e)}')

    def _read_env_vars(self):
        self.general.debug = getenv('DEBUG', self.config.get('debug', 'false').lower()).lower() == 'true'
        self.server.port = int(getenv('LISTEN_PORT', self.config.get('listen-port', 3343)))
        self.slave.quantity = int(getenv('SLAVES_QTY', self.config.get('slaves-qty', 1)))

    def __init__(self):
        try:
            if self.initialized:
                return
        except AttributeError:
            pass
        logging.debug('Config: init() called')
        try:
            self.config = {}
            self.general = Configuration.GeneralConfiguration()
            self.server = Configuration.ServerConfiguration()
            self.slave = Configuration.SlaveConfiguration()
            # read configs
            self._read_config_file()
            self._read_env_vars()
            logging.debug('Config: initialization done')
            self.initialized = True
        except AttributeError as e:
            logging.error(f'Config: initialization error: {str(e)}')
            exit(1)
