# ALL functions relating to the server/client MUST be created here!

import socket

def fCreateServer(port):
    # creates server connection to client and returns it
    lclSserverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lclServerSocket.bind(("", port))
    lclServerSocket.listen(1)
    lclConnection, lclClientAddress = clientSocket.accept()
    return lclConnection

def fReceiveFromClient():
    # receives key inputs from client

def fSendToClient():
    # sends key inputs to client

def fCreateClient(IP, port):
    # creates client connection to server and return the socket connecting them
    lclClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lclClientSocket.connect((IP, port))
    return lclClientSocket

def fReceiveFromServer():
    # receives key inputs from server

def fSendToServer():
    # sends key inputs to server
