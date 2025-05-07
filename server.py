import socket
import os
import mimetypes
from datetime import datetime

HOST = '127.0.0.1'
PORT = 8080
WWW_DIR = 'www'

def log_request(request_line, status_code):
    with open("log.txt", "a") as log:
        log.write(f"[{datetime.now()}] {request_line} -> {status_code}\n")

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    if not request:
        return
    lines = request.split('\r\n')
    request_line = lines[0]
    print(request_line)
    try:
        method, path, _ = request_line.split()
        if method != 'GET':
            client_socket.close()
            return

        if path == '/':
            path = '/index.html'

        filepath = os.path.join(WWW_DIR, path.lstrip('/'))
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
            content_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode() + content
            client_socket.sendall(response)
            log_request(request_line, 200)
        else:
            filepath = os.path.join('www', '404.html')
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    content = f.read()
            else:
                content = b"<h1>404 Not Found</h1>"
            
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode() + content
            
            client_socket.sendall(response)
            log_request(request_line, 404)            
    except Exception as e:
        print("Errore:", e)
    finally:
        client_socket.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server in ascolto su http://{HOST}:{PORT}")
        while True:
            client_socket, _ = server_socket.accept()
            handle_request(client_socket)

if __name__ == '__main__':
    start_server()
