import sys, socket
import echoserver2
import echoclient2

#port cannot be the same number every time. 
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('', 0))
addr, port = tcp.getsockname()
tcp.close()
#Source: https://gist.github.com/gabrielfalcao/20e567e188f588b65ba2
#Caitlin will write original code for this later.

question = input("Will you host, join, or quit?: ")

if question == "host":
    echoserver2.main(port)
elif question == "join":
    echoclient2.main()
else:
    print("\nGoodbye!")
