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

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

HOST = 'localhost'
PORT = 12345

class IRCClient(patterns.Subscriber):

    def __init__(self):
        super().__init__()
        self.username = str()
        self.msg = ""
        self._run = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        self.msg = msg
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):
        # Will need to modify this
        logger.info(f"In process input -> msg: {msg}")
        self.add_msg(msg)
        if msg.lower().startswith('/quit'):
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

    def send_msg(self,msg):
        self.sock.sendall("Something " + msg)

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    def connect(self, username):
        self.sock.connect((HOST,PORT))


    async def run(self):
        """
        Driver of your IRC Client
        """
        # Remove this section in your code, simply for illustration purposes
        #for x in range(10):
        #    self.add_msg(f"call after View.loop: {self.msg}")
        #    await asyncio.sleep(2)

        self.connect("Max")
        self.send_msg("Something from the client")


    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass



def main(args):
    # Pass your arguments where necessary
    client = IRCClient()
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
    args = None
    main(args)
