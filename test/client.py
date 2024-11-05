import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

if __name__ == "__main__":
    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = "test"
    byte = msg.encode()
    UDP_socket.sendto(byte, (SERVER_IP, SERVER_PORT))
