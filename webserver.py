from http.server import BaseHTTPRequestHandler, HTTPServer

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("<html><head><title>Mi Página</title></head>".encode())
        self.wfile.write("<body><h1>Hola Alejandro</h1></body></html>".encode())

def run(server_class=HTTPServer, handler_class=MyServer, port=9999):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run() #http://vicentedf.hopto.org/:9999