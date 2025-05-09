import socket
import os
import mimetypes
import threading
import logging

from numpy.f2py.auxfuncs import throw_error

HOST = '127.0.0.1'
PORT = 8080
WWW_DIR = 'www'
LOG_FILE = 'log.txt'

# --- Configure Logging ---
logger = logging.getLogger('web_server')
logger.setLevel(logging.INFO)

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

def log_request(request_line, status_code, client_address):
    logger.info(f"{client_address[0]}:{client_address[1]} - \"{request_line}\" {status_code}")

def read_file_content(filepath):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"'{filepath}' is not a regular file or does not exist.")
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except IOError as e:
        logger.error(f"IOError while reading file {filepath}: {e}")
        raise


def send_response(client_socket, status_code, content, content_type):
    status_texts = {
        200: "OK",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
    }
    status_text = status_texts.get(status_code, "Unknown Status")

    response = (
                   f"HTTP/1.1 {status_code} {status_text}\r\n"
                   f"Content-Type: {content_type}\r\n"
                   f"Content-Length: {len(content)}\r\n"
                   "Connection: close\r\n\r\n"
               ).encode() + content

    try:
        client_socket.sendall(response)
        return True
    except IOError as e:
        logger.error(f"Error sending response (status {status_code}) to client: {e}")
        return False
    except Exception as e:
        logger.exception(f"An unexpected error occurred while trying to send response (status {status_code}): {e}")
        return False

def handle_request(client_socket, address_info):
    try:
        request = client_socket.recv(4096).decode()
        if not request:
            return

        lines = request.split('\r\n')
        request_line = lines[0]
        method, path, _ = request_line.split()

        if method.upper() != 'GET':
            logger.info(f"HTTP method '{method}' not supported")
            send_response(client_socket, 405, b"<h1>405 Method Not Allowed</h1>", content_type="text/html")
            log_request(request_line, 405, address_info)
            return

        if path == '/':
            path = '/index.html'

        filepath = os.path.join(WWW_DIR, path.lstrip('/'))
        try:
            content = read_file_content(filepath)
            content_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
            send_response(client_socket, 200, content, content_type)
            log_request(request_line, 200, address_info)
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}")
            error_filepath = os.path.join(WWW_DIR, '404.html')
            try:
                content = read_file_content(error_filepath)
            except FileNotFoundError:
                logger.warning(f"Error file not found: {error_filepath}")
                content = b"<h1>404 Not Found</h1>"
            send_response(client_socket, 404, content, content_type="text/html")
            log_request(request_line, 404, address_info)
        except IOError as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            send_response(client_socket, 500, b"<h1>500 Internal Server Error</h1>", content_type="text/html")
            log_request(request_line, 500, address_info)

    except Exception as e:
        logger.exception(f"An unexpected error occurred while trying to handle request: {e}")
    finally:
        client_socket.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

        logger.info(f"Server listening on http://{HOST}:{PORT}")

        while True:
            client_socket, address_info = server_socket.accept()

            logger.info(f"Accepted connection from {address_info[0]}:{address_info[1]}. Creating new thread.")

            client_handler = threading.Thread(target=handle_request, args=(client_socket, address_info))
            client_handler.daemon = True
            client_handler.start()

if __name__ == '__main__':
    start_server()
