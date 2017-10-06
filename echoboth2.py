import sys, socket


question = input("Will you host, join, or quit?: ")


if question == "host":
    #Server
    #print("9877")
    IPAddr = socket.gethostbyname(socket.gethostname())
    print("Your IP is: " + IPAddr)
    port = 9878
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.bind((IPAddr, port))
    clientSocket.listen(1)
    connection, clientAddress = clientSocket.accept()
    while True:
        message = connection.recv(1024).decode()
        print(message)
    connection.send(message.encode())
elif question == "join":
    #port = int(input("What is the port? "))
    #Client
    #IPAddr = input("What is the IP address of the server? ")
    IPAddr = "35.40.131.44"
    port = 9878
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.connect((IPAddr, port))
    while True:
        message = input("Enter a message: ")
        serverSocket.send(message.encode())
        message = serverSocket.recv(1024).decode()
    print(message)
else:
    print("\nGoodbye!")



