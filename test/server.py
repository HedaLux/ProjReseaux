import socket
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345


if __name__ == "__main__":
    UDP_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_Socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Server is running on {SERVER_IP}:{SERVER_PORT}")
    time.sleep(20)

    while True:
        print("Server is waiting for message.")
        query, client_address = UDP_Socket.recvfrom(1024)
        print(f"message received from {client_address} -> {query}")