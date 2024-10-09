import socket
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

HOST = '127.0.0.1'
PORT = 8080


def handle_client_connection(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request received:\n{request}")

        if not request:
            return

        request_line = request.splitlines()[0]
        method, path, _ = request_line.split()

        parsed_url = urlparse(path)
        query_params = parse_qs(parsed_url.query)
        status_param = query_params.get('status', ['200'])[0]

        try:
            status_code = int(status_param)
            status_message = HTTPStatus(status_code).phrase
        except (ValueError, KeyError):
            status_code = 200
            status_message = 'OK'

        response_status = f"HTTP/1.1 {status_code} {status_message}\r\n"
        response_headers = [
            f"Request Method: {method}",
            f"Request Source: {client_socket.getpeername()}",
            f"Response Status: {status_code} {status_message}"
        ]

        for header_line in request.splitlines()[1:]:
            if header_line:
                response_headers.append(header_line)

        response_body = "\r\n".join(response_headers)

        response = (
                response_status +
                "Content-Type: text/plain\r\n" +
                f"Content-Length: {len(response_body)}\r\n" +
                "Connection: close\r\n" +
                "\r\n" +
                response_body
        )

        client_socket.sendall(response.encode('utf-8'))

    finally:
        client_socket.close()


def run_server():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Настраиваем TCP-сокет
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_client_connection(client_socket)


if __name__ == "__main__":
    run_server()