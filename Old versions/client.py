import socket

# Configura el cliente
ipaddr = "37.14.134.118" #IP pública en https://www.whatismyip.com/
port = 9999
print("Iniciando conexión al servidor", ipaddr, "en el puerto", port)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ipaddr, port))

while True:
    # Solicita al usuario que ingrese un mensaje
    message = input("Enter a message (or 'quit' to exit): ")
    if message == 'quit':
        break
    # Envía el mensaje al servidor
    client.send(message.encode())
    # Recibe la respuesta del servidor y la imprime
    response = client.recv(1024)
    print("Server response:", response.decode())

# Cierra la conexión con el servidor
client.close()