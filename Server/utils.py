import socket

def send_error_message_to(sock, client_address, message):
    sock.sendto({"result": "error", "message" : message}, client_address)