#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Read about environment variables in README.md

import logging

from os import getenv


class Configuration(object):
    singleton_object = None

    def __new__(cls, *args, **kwargs):
        if not Configuration.singleton_object:
            logging.debug('Config: creating new object')
            Configuration.singleton_object = super().__new__(cls, *args, **kwargs)
        return Configuration.singleton_object

    class CurlConfiguration:
        def __init__(self, urls):
            self.urls = urls

    class PingConfiguration:
        def __init__(self, urls):
            self.urls = urls

    class SmtpConfiguration:
        def __init__(self, server, port, user, password):
            self.server = server
            self.port = port
            self.user = user
            self.password = password
            self.configured = server and port and user and password

    class SlackConfiguration:
        def __init__(self, webhook_url):
            self.webhook_url = webhook_url
            self.configured = webhook_url and webhook_url

    class NotificationConfiguration:
        def __init__(self, enabled, interval, emails):
            self.enabled = enabled
            self.interval = interval
            self.emails = emails

    class CheckingConfiguration:
        def __init__(self, interval, fails_limit):
            self.interval = interval
            self.fails_limit = fails_limit

    def __init__(self):
        try:
            if self.initialized:
                return
        except AttributeError:
            pass
        logging.debug('Config: init() called')
        try:
            self.curl = self.CurlConfiguration(
                urls=list(filter(None, getenv('CURL', '').split(';;')))
            )
            self.ping = self.PingConfiguration(
                urls=list(filter(None, getenv('PING', '').split(';;')))
            )
            if not self.curl.urls and not self.ping.urls:
                raise Exception('Configuration: Neither curls nor pings were passed')
            self.smtp = self.SmtpConfiguration(
                server=getenv('SMTP_SERVER'),
                port=int(getenv('SMTP_PORT', 465)),
                user=getenv('SMTP_USER'),
                password=getenv('SMTP_PASSWORD')
            )
            self.slack = self.SlackConfiguration(
                webhook_url=getenv('SLACK_WEBHOOK_URL')
            )
            self.notification = self.NotificationConfiguration(
                enabled=getenv('NOTIFICATION_ENABLED', 'true').lower() != 'false',
                interval=int(getenv('NOTIFICATION_INTERVAL', 5)),
                emails=list(filter(None, getenv('EMAILS', '').split(';;')))
            )
            self.checking = self.CheckingConfiguration(
                interval=int(getenv('CHECK_INTERVAL', 10)),
                fails_limit=int(getenv('FAILS_LIMIT', 3))
            )
            logging.info(f"Config: curl urls: {self.curl.urls}")
            logging.info(f"Config: ping urls: {self.ping.urls}")
            logging.info(f"Config: notification emails: {self.notification.emails}")
            self.initialized = True
        except AttributeError as e:
            logging.error(f'Config: initialization error: {str(e)}')
            exit(1)
