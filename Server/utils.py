import socket
import json

def send_message_to(sock, client_address, type, message):
    messageJson = {"response": type, "message" : message}

    message = json.dumps(messageJson)

    try:
        sock.sendto(message.encode(), client_address)
    except ConnectionResetError:
        print(f"l'hôte : {client_address} a fermé la connection avant de recevoir la réponse")