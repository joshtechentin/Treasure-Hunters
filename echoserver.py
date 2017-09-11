import sys, socket

IPAddr = socket.gethostbyname(socket.gethostname())
port = 9878
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.bind((IPAddr, port))
clientSocket.listen(1)
connection, clientAddress = clientSocket.accept()
while True:
    message = connection.recv(1024).decode()
    print(message)
    connection.send(message.encode())
