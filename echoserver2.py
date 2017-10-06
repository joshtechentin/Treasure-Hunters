import sys, socket

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('', 0))
addr, port = tcp.getsockname()
tcp.close()

def main(port):
    print(port)
    IPAddr = socket.gethostbyname(socket.getfqdn())
    print("Your IP is: " + IPAddr)
    #port = 9878
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.bind((IPAddr, port))
    clientSocket.listen(1)
    connection, clientAddress = clientSocket.accept()
    while True:
        message = connection.recv(1024).decode()
        if message != "quit":
            print(message)
            message = "Message received."
            connection.send(message.encode())
        else:
            print(message)
            connection.send(message.encode())
            print("\nGoodbye!")
            break
