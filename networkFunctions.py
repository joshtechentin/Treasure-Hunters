# ALL functions relating to the server/client MUST be created here!

import socket, pickle, pygame

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
    return data

def fSendToClient(lclConnection, data):
    # sends key inputs to client
    lclConnection.sendall(data.encode())

def fSendMapToClient(lclConnection, grid):
    rows = len(grid)
    cols = len(grid[0])
    print(rows)
    print(cols)
    
    row = str(rows)
    col = str(cols)

    #fSendToClient(lclConnection, row)
    #fSendToClient(lclConnection, col)
    
    print("Sending grid...")

    for r in range(rows):
        for c in range(cols):
            print(grid[r][c])
            grid[r][c].image = 0
            data = pickle.dumps(grid[r][c])
            lclConnection.sendall(data)
            grid[r][c].image = pygame.image.load("images/terrain/"+grid[r][c].name+".png")
            status = fReceiveFromClient(lclConnection)
            if status != "READYFORNEXT":
                print("There was an error..")
                break #Not ideal, but good enough for now

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
    return data

def fReceiveIntFromServer(lclClientSocket):
    # receives key inputs from server
    data = lclClientSocket.recv(4).decode('utf-8')
    return data

def fReceiveMapFromServer(lclClientSocket):
    #rows = fReceiveIntFromServer(lclClientSocket)
    #cols = fReceiveIntFromServer(lclClientSocket)

    rows = 33 #int(rows)
    cols = 33 #int(cols)
    print(rows)
    print(cols)

    grid = []

    print("Receiving grid...")

    for r in range(rows):
        for c in range(cols):
            if c == 0:
                grid.append([])
            data = lclClientSocket.recv(4096)
            gridData = pickle.loads(data)
            grid[r].append(gridData)
            grid[r][c].image = pygame.image.load("images/terrain/"+grid[r][c].name+".png")
            print(grid[r][c])
            fSendToServer(lclClientSocket, "READYFORNEXT")


    return grid

def fSendToServer(lclClientSocket, data):
    # sends key inputs to server
    lclClientSocket.sendall(data.encode())

def fCloseClient(lclClientSocket):
    lclClientSocket.close()
