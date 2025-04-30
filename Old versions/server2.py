import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 9999)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('Connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            print("Waiting response...")
            data = connection.recv(255)
            print('<- Received {!r}'.format(data))
            if data:
                print('Sending data back to the client')
                message = 'Hola Cliente'
                connection.sendall(message.encode('utf-8'))
            else:
                print('No data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()