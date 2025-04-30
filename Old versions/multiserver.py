import socket
import threading

# Función para manejar las conexiones de los clientes
def handle_client(client_socket):
    while True:
        # Recibe los datos del cliente
        request = client_socket.recv(1024)
        if not request:
            break
        # Procesa los datos recibidos (en este caso, simplemente los imprime)
        print("Received:", request.decode())
        # Envía una respuesta al cliente
        client_socket.send("Received message\n".encode())
    # Cierra la conexión con el cliente
    client_socket.close()

# Configura el servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9999)) #0.0.0.0 Permite al servidor aceptar conexiones desde cualquier dirección IP asociada con la máquina, ya sea local o externa. "localhost" solo permite recibir conexiones a la IP local (127.0.0.1)
server.listen(5)
print("Server listening on port 9999")

# Ciclo principal para aceptar conexiones de los clientes
while True:
    client_socket, _ = server.accept()
    print("Accepted connection from:", client_socket.getpeername())
    # Crea un nuevo hilo para manejar la conexión con el cliente
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()