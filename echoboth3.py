import sys, socket

question = input("Will you host, join, or quit?: ")
#port = 80

#port cannot be the same number every time. 
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('', 0))
addr, port = tcp.getsockname()
tcp.close()
#Source: https://gist.github.com/gabrielfalcao/20e567e188f588b65ba2
#Caitlin will write original code for this later.


if question == "host":
    #Server
    IPAddr = socket.gethostbyname(socket.getfqdn())
    print("Your IP is: " + IPAddr)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    clientSocket.bind((IPAddr, port))

    flag = True
    while flag:
        try:
            clientSocket.settimeout(20) #Time server waits for client in seconds
            clientSocket.listen(1) 
            connection, clientAddress = clientSocket.accept() 
        except socket.timeout:
            print("Client failed to connect in time.")
            clientSocket.close()
            break
        except:
            print("\nError as occurred:")
            raise
        else:
            while True:
                connection.setblocking(1)
                message = connection.recv(1024).decode()
                if message != "quit":
                    print(message)
                    message = "message received."
                    connection.send(message.encode())
                else:
                    print(message)
                    connection.send(message.encode())
                    clientSocket.close()
                    print("\nServer socket closed. Goodbye!")
                    break
            flag = False
elif question == "join":
    #Client
    IPAddr = input("What is the IP address of the server? ")
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
            serverSocket.close()
            print("\nGoodbye!")
            break
else:
    print("\nGoodbye!")

