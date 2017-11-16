# ALL functions relating to the server/client MUST be created here!
# ALL functions relating to the server/client MUST be created here!

import socket, pickle, pygame

WHITE = (255, 255, 255)

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
    data = lclConnection.recv(1024).decode('utf-8')
    if data == "DATAISEMPTY":
        data = ""
    return data

def fReceiveIntFromClient(lclConnection):
    # receives key inputs from server
    intData = lclConnection.recv(4096)
    data = pickle.loads(intData)
    return data

def fSendToClient(lclConnection, data):
    # sends key inputs to client
    if data == "":
        data = "DATAISEMPTY"
    lclConnection.sendall(data.encode())

def fSendIntToClient(lclConnection, data):
    intData = pickle.dumps(data)
    lclConnection.sendall(intData)

def fSendMapToClient(lclConnection, grid):
    rows = len(grid)
    cols = rows
    
    fSendIntToClient(lclConnection, rows)

    for r in range(rows):
        for c in range(cols):
            grid[r][c].image = 0
            if grid[r][c].treasure != 0:
                grid[r][c].treasure.image = 0
            data = pickle.dumps(grid[r][c])
            lclConnection.sendall(data)
            grid[r][c].image = pygame.image.load("images/terrain/" + grid[r][c].name + ".png")
            if grid[r][c].treasure != 0:
                grid[r][c].treasure.image = pygame.image.load("images/treasure/" + grid[r][c].treasure.name + ".png").convert()
                grid[r][c].treasure.image.set_colorkey(WHITE)
            status = fReceiveFromClient(lclConnection)
            if status != "READYFORNEXT":
                print("There was an error..")
                break # Not ideal, but good enough for now

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
    data = lclClientSocket.recv(1024).decode('utf-8')
    if data == "DATAISEMPTY":
        data = ""
    return data

def fReceiveIntFromServer(lclClientSocket):
    # receives key inputs from server
    intData = lclClientSocket.recv(4096)
    data = pickle.loads(intData)
    return data

def fReceiveMapFromServer(lclClientSocket):
    rows = fReceiveIntFromServer(lclClientSocket)
    cols = rows

    grid = []

    for r in range(rows):
        for c in range(cols):
            if c == 0:
                grid.append([])
            data = lclClientSocket.recv(4096)
            gridData = pickle.loads(data)
            grid[r].append(gridData)
            grid[r][c].image = pygame.image.load("images/terrain/" + grid[r][c].name + ".png")
            if grid[r][c].treasure != 0:
                grid[r][c].treasure.image = pygame.image.load("images/treasure/" + grid[r][c].treasure.name + ".png").convert()
                grid[r][c].treasure.image.set_colorkey(WHITE)
            fSendToServer(lclClientSocket, "READYFORNEXT")


    return grid

def fSendToServer(lclClientSocket, data):
    # sends key inputs to server
    if data == "":
        data = "DATAISEMPTY"
    lclClientSocket.sendall(data.encode())

def fSendIntToServer(lclClientSocket, data):
    intData = pickle.dumps(data)
    lclClientSocket.sendall(intData)

def fCloseClient(lclClientSocket):
    lclClientSocket.close()
