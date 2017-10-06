tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('', 0))
addr, port = tcp.getsockname()
tcp.close()

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
