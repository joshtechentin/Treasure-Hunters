import sys, socket

stopper = 0
question = input("Will you host, join, or quit?: ")

while stopper == 0:
    if question == "host":
        stopper = 1
        #Server 
        IPAddr = ""
        port = 9878
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.bind((IPAddr, port))
        clientSocket.listen(1)
        connection, clientAddress = clientSocket.accept()
        while True:
            message = connection.recv(1024).decode()
            if message != "quit":
                print(message)
                connection.send(message.encode())
            else:
                print(message)
                connection.send(message.encode())
                print("\nGoodbye!")
                break
    elif question == "join":
        stopper = 1
        #Client
        IPAddr = "35.40.130.131" 
        port = 9878
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.connect((IPAddr, port))
        while True:
            message = input("Enter a message: ")
            if message != "quit":
                serverSocket.send(message.encode())
                message = serverSocket.recv(1024).decode()
                #print(message)
            else:
                serverSocket.send(message.encode())
                message = serverSocket.recv(1024).decode()
                #(message)
                print("\nGoodbye!")
                break
    elif question == "quit":
        stopper = 1
    else:
        stopper = 0
