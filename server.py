import socket
import os
import mimetypes
from datetime import datetime
import logging

HOST = '127.0.0.1'
PORT = 8080
WWW_DIR = 'www'
LOG_FILE = 'log.txt'

# --- Configure Logging ---
logger = logging.getLogger('web_server')
logger.setLevel(logging.INFO)

def log_request(request_line, status_code):
    with open("log.txt", "a") as log:
        log.write(f"[{datetime.now()}] {request_line} -> {status_code}\n")
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
# --- End Logging Configuration ---


def read_file_content(filepath):
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except (FileNotFoundError, IOError) as e:
        print(f"Error reading file {filepath}: {e}")
        return b""

def send_response(client_socket, status_code, content, content_type):
    status_text = "OK" if status_code == 200 else "Not Found"
    response = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(content)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode() + content
    client_socket.sendall(response)

def handle_request(client_socket):
    request = client_socket.recv(4096).decode()
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
            content = read_file_content(filepath)
            content_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'

            send_response(client_socket, 200, content, content_type)

            log_request(request_line, 200)
        else:
            filepath = os.path.join('www', '404.html')
            if os.path.exists(filepath):
                content = read_file_content(filepath)
            else:
                content = b"<h1>404 Not Found</h1>"

            send_response(client_socket, 404, content, content_type="text/html")

            log_request(request_line, 404)
    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server listening on http://{HOST}:{PORT}")
        while True:
            client_socket, _ = server_socket.accept()
            handle_request(client_socket)

if __name__ == '__main__':
    start_server()
