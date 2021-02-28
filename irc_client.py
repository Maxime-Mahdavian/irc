#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import asyncio
import logging

import patterns
import view
import socket
import argparse
from _thread import *

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

#HOST = 'localhost'
#PORT = 12345

class IRCClient(patterns.Subscriber):

    def __init__(self, host, port):
        super().__init__()
        self.username = ""
        self.msg = ""
        self._run = True
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, int(self.port)))


    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")

        if not self.username:
            nick_message = "NICK " + msg
            self.send_msg(nick_message)
            self.set_nickname(msg)
        else:
            self.process_input(msg)
            self.send_msg(msg)



    def process_input(self, msg):
        # Will need to modify this
        logger.info(f"In process input -> msg: {msg}")
        #self.add_msg(msg)
        if msg.lower().startswith('/quit'):
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

    def send_msg(self, msg):
        self.sock.sendall(bytes(msg.encode()))

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    def connect(self, username):
        self.sock.connect((HOST,PORT))

    def set_nickname(self,nick):
        self.username = nick

    def listenToRespone(self):
        while True:
            response = self.sock.recv(1024)
            self.add_msg(response.decode('utf-8'))


    async def run(self):
        """
        Driver of your IRC Client
        """
        self.add_msg("Type your nickname")
        # Remove this section in your code, simply for illustration purposes
        #for x in range(10):
        #    self.add_msg(f"call after View.loop: {self.msg}")
        #    await asyncio.sleep(2)
        start_new_thread(self.listenToRespone, ())


    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass



def main(args):
    # Pass your arguments where necessary
    client = IRCClient(args[0], args[1])
    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")
        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )
        try:
            asyncio.run( inner_run() )
        except KeyboardInterrupt as e:
            logger.debug(f"Signifies end of process")
    client.close()

if __name__ == "__main__":
    # Parse your command line arguments here
    parser = argparse.ArgumentParser()

    parser.add_argument('--server', '-s', default='127.0.0.1', help='server IP address')
    parser.add_argument('-p', '--port', default='12345', help='server port')

    args = parser.parse_args()
    HOST = args.server
    PORT = args.port

    cmdArgs = [HOST, PORT]
    main(cmdArgs)
