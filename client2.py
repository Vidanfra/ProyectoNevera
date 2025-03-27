import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
#Es necesario configurar el puerto en el router y desactivar el firewall (y reiniciar el router)
server_address = ('37.14.134.118', 9999) 
#server_address = ('localhost', 9999)
print('Connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:
    while True:
        # Send data
        message = 'Hola Servidor'
        print('-> Sending: {!r}'.format(message))
        sock.sendall(message.encode('utf-8'))

        # Look for the response
        data = sock.recv(255)
        print('<- Received:  {!r}'.format(data))

finally:
    print('Closing socket')
    sock.close()