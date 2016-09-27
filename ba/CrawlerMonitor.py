# coding=utf-8

import socket
import uuid


class CrawlerMonitor(object):

    def __init__(self):
        pass

    def run(self):
        pass


def get_localhost():
    return socket.gethostbyname(socket.gethostname())


def get_mac_addr():
    return uuid.UUID(int=uuid.getnode()).hex[-12:]

if __name__ == '__main__':
    print socket.gethostbyname(socket.gethostname())
    print get_mac_addr()
    # monitor = CrawlerMonitor()
    # monitor.run()
