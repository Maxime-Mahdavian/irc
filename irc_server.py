import socket
import re
import logging
from _thread import *
import threading
import argparse

HOST = ''

# Regex to determine if the nickname or the command received is of the right form
nickname_command_regex = ':?\w*\s?NICK\s*\w*'
nickname_regex = '^[a-zA-Z][a-zA-Z\d\-\[\]\\\'\^\{\}]*$'
privmsg_regex = '^PRIVMSG\s\w+\s:.+$'

# Numeric replies of the server
RPL_WELCOME = '001'
ERR_UNKNOWNCOMMAND = '421'
ERR_ERRONEUSNICKNAME = '432'
ERR_NICKCOLLISION = '436'
ERR_NEEDMOREPARAMS = '461'

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

# Parse the command line argument
parser = argparse.ArgumentParser()

# Default port is 12345
parser.add_argument('-p', '--port', default='12345', help='server port')

args = parser.parse_args()
PORT = args.port

# Initialization of important variables and the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, int(PORT)))
sock.listen(10)
numberOfThread = 0
clients = set()
clients_lock = threading.Lock()


# Data structure to hold client information that are connected to the server
# Contains the connection info and the nickname of the clients, since we need
# to make sure that no two people have the same nickname
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


# Function running in the thread to listen to all clients connected to the server
# It runs until the client disconnects and parse the commands received by the client
def listenForClients(client):
    global numberOfThread
    while True:
        data = client.getConn().recv(512)
        if not data: continue

        # Decode the message and remove the \r\n from the message for easier parsing
        msg = data.decode('utf-8')
        msg = msg[:len(msg) - 2]
        print(msg)

        # Branch if the command is a nickname
        if re.match(nickname_command_regex, msg):
            # print("This is a nickname: " + data.decode('utf-8'))

            # If the first character of the command is :, then it is a request for a nickname change
            if msg[0] == ':':
                print("This is a change of nickname")
                print_all_clients()
                new_nickname = msg[msg.find("NICK") + 5:]

                # Let's check if the new nickname is correct, if it is not, then we send error
                # If it is empty, then there were no parameter, or it might not be a valid nickname
                if not new_nickname:
                    send_to_client(ERR_NEEDMOREPARAMS, client.getConn())
                    continue
                elif not re.match(nickname_regex, new_nickname):
                    send_to_client(ERR_ERRONEUSNICKNAME, client.getConn())
                    continue

                old_nickname = msg[1:msg.find("NICK") - 1]

                # We need to check if the nickname already exists
                if check_for_nickname(new_nickname):
                    for x in clients:
                        if x.getNickname() == old_nickname:
                            x.setNickname(new_nickname)
                            break
                broadcast("SERVER: User " + old_nickname + " has changed nickname to: " + new_nickname,
                          client.getNickname(), "server")

            # Otherwise, it is a normal nickname command
            else:
                client_nickname = msg[5:]

                # If the nickname is not valid, we respond with an error
                if not re.match(nickname_regex, client_nickname):
                    send_to_client(ERR_ERRONEUSNICKNAME, client.getConn())
                    continue

                # Check if the nickname already exist
                if check_for_nickname(client_nickname):
                    client.setNickname(client_nickname)
                    print(client.getNickname())
                    logger.info(f"SERVER: this is the nickname {client.getNickname()}")
                    send_to_client(RPL_WELCOME, client.getConn())
                else:
                    send_to_client(ERR_NICKCOLLISION, client.getConn())

        # Branch if the command is a message
        elif re.match(privmsg_regex, msg):
            privmsg = msg[msg.find(":") + 1:]
            print(client.getNickname() + ": " + privmsg)
            broadcast(privmsg, client.getNickname())
            # logger.info("After sendall in server")

        # Branch if it is a quit command from the client to disconnect
        # We remove the client for our list and tell the client it is okay to stop
        elif msg == '/quit':
            remove_client(client.getNickname())
            numberOfThread -= 1
            logger.info("One of the server thread has closed")
            send_to_client("KILL", client.getConn())
            client.getConn().close()
            break

        # This branch is if the command entered is not recognized by the server
        else:
            send_to_client(ERR_UNKNOWNCOMMAND, client.getConn())


# Broadcast msg to every client connected to the server
# The sender is the client sending the message, used for formatting purposes
# The flag argument is used by the server for formatting purposes
def broadcast(msg, sender, flag=""):
    # logger.info(f"Nickname in broacast {nickname}")
    for x in clients:
        if x.getNickname() == sender or flag == "server":
            message = msg
        else:
            message = sender + ": " + msg

        try:
            x.getConn().sendall(bytes(message.encode()))
        except IOError as e:
            logger.error(e)


# Send msg to the client with connection conn
def send_to_client(msg, conn):
    try:
        conn.sendall(bytes(msg.encode()))
    except IOError as e:
        logger.error(e)


# Check if the nickname 'nickname' is not already connected to the server
def check_for_nickname(nickname):
    for x in clients:
        if x.getNickname() == nickname:
            return False

    return True


# Print every client connected to the sever, used for debugging purposes
def print_all_clients():
    print("List of clients")
    for x in clients:
        print(x.getNickname())


# Remove client from the list of clients connected to the server
def remove_client(nickname):
    for x in clients:
        if x.getNickname() == nickname:
            with clients_lock:
                clients.remove(x)
            break


# Continuously look for incoming client connections
# When a connection is accepted, we add the client to the list of connected clients
# Then, we start a new thread that runs the function listenForClients to listen for commands
while True:
    conn, addr = sock.accept()
    print('Connected by', addr)
    with clients_lock:
        clientInfo = ClientInfo(conn)
        clients.add(clientInfo)
    numberOfThread += 1
    start_new_thread(listenForClients, (clientInfo,))
    print(numberOfThread)
