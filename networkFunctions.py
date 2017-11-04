# ALL functions relating to the server/client MUST be created here!

import socket, pickle

##Server start
def fGetIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    IP = s.getsockname()[0]
    s.close()
    return IP    

def fCreateServer(port):
    # creates server connection to client and returns it
    lclServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lclServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    lclServerSocket.bind(('', port)) 
    lclServerSocket.listen(1)
    return lclServerSocket

def fCreateConnection(lclServerSocket):
    lclConnection, lclClientAddress = lclServerSocket.accept()
    return lclConnection

def fReceiveFromClient(lclConnection):
    # receives key inputs from client
    data = lclConnection.recv(1024).decode()
    return data

def fSendToClient(lclConnection, data):
    # sends key inputs to client
    lclConnection.sendall(data.encode())

def fSendMapToClient(lclConnection, grid):
    gridData = pickle.dumps(grid)
    lclConnection.sendall(gridData)

def fCloseServer(lclServerSocket):
    lclServerSocket.close()
    
##Client start
def fCreateClient(IP, port):
    # creates client connection to server and return the socket connecting them
    lclClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lclClientSocket.connect((IP, port))
    return lclClientSocket

def fReceiveFromServer(lclClientSocket):
    # receives key inputs from server
    data = lclClientSocket.recv(1024).decode()
    return data

def fReceiveMapFromServer(lclClientSocket):
    gridData = lclClientSocket.recv(4096)
    grid = pickle.loads(gridData)
    return grid

def fSendToServer(lclClientSocket, data):
    # sends key inputs to server
    lclClientSocket.sendall(data.encode())

def fCloseClient(lclClientSocket):
    lclClientSocket.close()
