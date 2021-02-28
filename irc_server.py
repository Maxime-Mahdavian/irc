import socket
import sys
import re
import logging
import patterns
import irc_client
import view
from _thread import *
import threading

HOST = ''
PORT = 12345

nick = '^NICK\s.+$'

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(10)
numberOfThread = 0
clients = set()
clients_lock = threading.Lock()


def listenForClients(conn):

    while True:
        data = conn.recv(1024)
        if not data: continue
        msg = data.decode('utf-8')
        if re.match(nick, msg):
            print("This is a nickname: " + data.decode('utf-8'))
            conn.sendall(data)

        else:
            # logger.info(f"SERVER NICK REGEX: {nick}")
            # logger.info(f"SERVER MSG: {str(msg)}")
            # result = re.match(nick, data.decode('utf-8'))
            # logger.info(f"SERVER REGEX RESULT: {result}")
            print(msg)
            broadcast(msg)
            #logger.info("After sendall in server")


# if __name__ == "__main__":
#     IRCServer = IRCServer()

def broadcast(msg):
    for x in clients:
        x.sendall(bytes(msg.encode()))

while True:
    conn, addr = sock.accept()
    print('Connected by', addr)
    with clients_lock:
        clients.add(conn)
    numberOfThread += 1
    start_new_thread(listenForClients, (conn,))
    print(numberOfThread)
