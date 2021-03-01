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

nickname_regex = ':?\w*\s?NICK\s\w+'
privmsg_regex = '^PRIVMSG\s\w+\s:.+$'

RPL_WELCOME          = '001'
ERR_NOSUCHNICK       = '401'
ERR_NOSUCHCHANNEL    = '403'
ERR_CANNOTSENDTOCHAN = '404'
ERR_UNKNOWNCOMMAND   = '421'
ERR_ERRONEUSNICKNAME = '432'
ERR_NICKNAMEINUSE    = '433'
ERR_NICKCOLLISION    = '436'
ERR_NEEDMOREPARAMS   = '461'

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(10)
numberOfThread = 0
clients = set()
clients_lock = threading.Lock()


class ClientInfo:

    def __init__(self, conn):
        self.conn = conn
        self.nickname = ""

    def getConn(self):
        return self.conn

    def getNickname(self):
        return self.nickname

    def setNickname(self, newNick):
        self.nickname = newNick


def listenForClients(client):

    while True:
        data = client.getConn().recv(512)
        if not data: continue
        msg = data.decode('utf-8')
        msg = msg[:len(msg)-2]
        print(msg)
        if re.match(nickname_regex, msg):
            #print("This is a nickname: " + data.decode('utf-8'))

            if msg[0] == ':':
                print("This is a change of nickname")
                new_nickname = msg[msg.find("NICK")+5:]
                old_nickname = msg[1:msg.find("NICK")-1]
                if check_for_nickname(new_nickname):
                    for x in clients:
                        if x.getNickname() == old_nickname:
                            x.setNickname(new_nickname)
                            break
                broadcast("SERVER: User " + old_nickname + " has changed nickname to: " + new_nickname, client.getNickname())


            else:
                client_nickname = msg[5:]

                if check_for_nickname(client_nickname):
                    client.setNickname(client_nickname)
                    print(client.getNickname())
                    logger.info(f"SERVER: this is the nickname {client.getNickname()}")
                    client.getConn().sendall(bytes(RPL_WELCOME.encode()))
                else:
                    client.getConn().sendall(bytes(ERR_NICKCOLLISION.encode()))

        elif re.match(privmsg_regex, msg):
            privmsg = msg[msg.find(":")+1:]
            print(client.getNickname() + ": " + privmsg)
            broadcast(privmsg, client.getNickname())
            #logger.info("After sendall in server")


# if __name__ == "__main__":
#     IRCServer = IRCServer()

def broadcast(msg, sender):
    #logger.info(f"Nickname in broacast {nickname}")
    for x in clients:
        if x.getNickname() == sender:
            message = msg
        else:
            message = sender + ": " + msg

        x.getConn().sendall(bytes(message.encode()))


def check_for_nickname(nickname):

    for x in clients:
        if x.getNickname() == nickname:
            return False

    return True



while True:
    conn, addr = sock.accept()
    print('Connected by', addr)
    with clients_lock:
        clientInfo = ClientInfo(conn)
        clients.add(clientInfo)
    numberOfThread += 1
    start_new_thread(listenForClients, (clientInfo,))
    print(numberOfThread)
