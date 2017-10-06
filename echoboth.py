import sys, socket

#port cannot be the same number every time. 
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('', 0))
addr, port = tcp.getsockname()
tcp.close()
#Source: https://gist.github.com/gabrielfalcao/20e567e188f588b65ba2
#Caitlin will write original code for this later.

question = input("Will you host, join, or quit?: ")


if question == "host":
    #Server
    print(port)
    IPAddr = socket.gethostbyname(socket.getfqdn())
    print("Your IP is: " + IPAddr)
    #port = 9877
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.bind((IPAddr, port))
    clientSocket.listen(1)
    connection, clientAddress = clientSocket.accept()
    while True:
        message = connection.recv(1024).decode()
        if message != "quit":
            print(message)
            message = "message received."
            connection.send(message.encode())
        else:
            print(message)
            connection.send(message.encode())
            print("\nGoodbye!")
            break
elif question == "join":
    port = int(input("What is the port? "))
    #Client
    IPAddr = input("What is the IP address of the server? ")
    #port = 9877
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.connect((IPAddr, port))
    while True:
        message = input("Enter a message: ")
        if message != "quit":
            serverSocket.send(message.encode())
            message = serverSocket.recv(1024).decode()
            print(message)
        else:
            serverSocket.send(message.encode())
            message = serverSocket.recv(1024).decode()
            print("\nGoodbye!")
            break
else:
    print("\nGoodbye!")


