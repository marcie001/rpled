#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import SocketServer
import os
import signal
import threading
import time

class MyTCPServer(SocketServer.TCPServer):

    def __init__(self, server_address, handler_class, bcm):
        self.bcm = bcm
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
        return

    def server_close(self):
        GPIO.cleanup(self.bcm)
        return SocketServer.TCPServer.server_close(self)


class MyTCPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        while True:
            data = self.rfile.readline().strip().split()
            if data[0] == 'ON':
                GPIO.output(self.server.bcm, True) 
                if len(data) > 1:
                    try:
                        interval = int(data[1])
                        if interval >= 0:
                            time.sleep(interval)
                            GPIO.output(self.server.bcm, False)
                    except ValueError:
                        pass
                self.wfile.write('OK\n')
            elif data[0] == 'OFF':
                GPIO.output(self.server.bcm, False)
                self.wfile.write('OK\n')
            elif data[0] == 'FLASH':
                count = 1
                if len(data) > 1:
                    try:
                        count = int(data[1])
                    except ValueError:
                        pass

                for _ in xrange(count):
                    GPIO.output(self.server.bcm, True) 
                    time.sleep(0.5)
                    GPIO.output(self.server.bcm, False)
                    time.sleep(0.2)

                self.wfile.write('OK\n')
            elif data[0] == 'QUIT':
                return
            else:
                self.wfile.write('COMMANDS: ON OFF FLASH QUIT\n')
            
if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = os.getenv('PORT', 9900)
    bcm = int(os.getenv('BCM', '5'))

    # initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup(bcm)
    GPIO.setup(bcm, GPIO.OUT)

    # Create the server
    server = MyTCPServer((host, port), MyTCPHandler, bcm)

    try:
        server.serve_forever()
    finally:
        server.server_close()

