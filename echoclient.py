import sys, socket

IPAddr = socket.gethostbyname(socket.gethostname())
port = 9878
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.connect((IPAddr, port))
while True:
    message = input("Enter a message: ")
    serverSocket.send(message.encode())
    message = serverSocket.recv(1024).decode()
    print(message)
