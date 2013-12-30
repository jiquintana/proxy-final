#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number
import sys
if sys.version_info < (3, 0):
    python_OldVersion = True
else:
    python_OldVersion = False

if python_OldVersion:       # Python version 2.7
    from Queue import Queue
    from SocketServer import TCPServer

else:                       # Python version 3.x
    from queue import Queue
    from socketserver import TCPServer

import threading, socket, os, time

from Proxy import Proxy
from ThreadPool import ThreadPoolMixIn
from Log import Log
import requests
from Config import Config

logger = Log()

class ThreadedServer(ThreadPoolMixIn, TCPServer):
    pass

def run(HandlerClass = Proxy,
        ServerClass = ThreadedServer,
        protocol="HTTP/1.0"):
    '''
    Run an HTTP server on port Config.PORT
    '''

    port = Config.PORT
    server_address = ('', port)

    HandlerClass.protocol_version = protocol
    RQServer = ServerClass(server_address, HandlerClass)
    Proxy.threadServer = RQServer

    sa = RQServer.socket.getsockname()

    try:
        RQServer.serve_forever()

    except KeyboardInterrupt:
        logger.pdebug("Catched Ctrl+C, trying to shutdown...")
        #RQServer.server_close()
        RQServer.force_shutdown()
        #os._exit(1)

    #RQHandler.serve_forever()


if __name__ == '__main__':
    run()