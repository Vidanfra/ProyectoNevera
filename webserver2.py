from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import sys
import threading
import time
import signal #DEP

TCP_connected = False
TCP_addr = ""

class MyServer(BaseHTTPRequestHandler):
    # Variables para contar las visitas y el número de mensajes
    visit_count = 0

    def do_GET(self):
         # Incrementa el contador de visitas cada vez que se recibe una solicitud GET
        MyServer.visit_count += 1

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Crea el contenido HTML de la página con el contador de visitas
        if TCP_connected:
            html_content = """
            <html>
            <head><title>Mi Página</title></head>
            <body>
                <h1>Vicente Danvila</h1>
                <p>Has visitado esta página {} veces.</p>
                <p>Cliente TCP conectado con IP {}.</p>
            </body>
            </html>
            """.format(MyServer.visit_count, TCP_addr)
        else:
            html_content = """
            <html>
            <head><title>Mi Página</title></head>
            <body>
                <h1>Vicente Danvila</h1>
                <p>Has visitado esta página {} veces.</p>
                <p>Cliente TCP no conectado.</p>
            </body>
            </html>
            """.format(MyServer.visit_count)

        self.wfile.write(html_content.encode())

def HTTP_server(server_class=HTTPServer, handler_class=MyServer, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server HTTP on port {port}...')
    httpd.serve_forever()

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def TCP_server(server):
    # Configura el servidor
    port = 9999
    server.bind(("0.0.0.0", port)) #0.0.0.0 Permite al servidor aceptar conexiones desde cualquier dirección IP asociada con la máquina, ya sea local o externa. "localhost" solo permite recibir conexiones a la IP local (127.0.0.1)
    server.listen(5)
    print("Server TCP listening on port", port)

    # Ciclo principal para aceptar conexiones de los clientes
    while True:
        client_socket, _ = server.accept()
        print("Accepted connection from:", client_socket.getpeername())
        global TCP_addr
        TCP_addr = client_socket.getpeername()
        # Crea un nuevo hilo para manejar la conexión con el cliente
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

# Función para manejar las conexiones de los clientes
def handle_client(client_socket):
    try:
        while True:
            # Recibe los datos del cliente
            request = client_socket.recv(1024)
            if not request:
                break
            # Procesa los datos recibidos (en este caso, simplemente los imprime)
            print("Received:", request.decode())
            global TCP_connected
            TCP_connected = True
            time.sleep(1)
            # Envía una respuesta al cliente
            client_socket.send("Received message\n".encode())
    except:
        print("Se ha producido una excepción!")
        
    finally:
        # Cierra la conexión con el cliente
        print("Connection with", client_socket.getpeername(),"client closed.")
        TCP_connected = False
        client_socket.close()

def custom_signal_handler(sig, frame, threads):
    def signal_handler (sig, frame):
        print("You pressed Ctrl+C!")
        print("Closing server...")
        for threads in thread:
            thread.close()

        return signal_handler
    
    sys.exit(0)

    

if __name__ == '__main__':
   
    HTTP_thread = threading.Thread(target=HTTP_server)
    TCP_thread = threading.Thread(target=TCP_server, args=(tcp_server,))

    threads_array = []
    threads_array.append(HTTP_thread)
    threads_array.append(TCP_thread)

    signal.signal(signal.SIGINT, custom_signal_handler(threads_array))
                                  
    HTTP_thread.start()
    TCP_thread.start()  

    HTTP_thread.join()
    TCP_thread.join()

