import socket
import json
from enum import Enum

class Status(Enum):
    INMENU = 1
    INGAME = 2

def send_message_to(sock, client_address, type, message):
    messageJson = {"response": type, "message" : message}

    message = json.dumps(messageJson)

    try:
        sock.sendto(message.encode(), client_address)
    except ConnectionResetError:
        print(f"l'hôte : {client_address} a fermé la connection avant de recevoir la réponse")

buffers = {}

def recevoir_message(sock, addr):
    global buffers
    
    if(addr not in buffers):
        buffers[addr] = b""

    try:
        while True:
            data = sock.recv(1024)
            if not data:
                return None
            buffers[addr] += data
            # Vérifier si le séparateur '\n' est présent dans le buffer
            if b'\n' in buffers[addr]:
                message_complet, buffers[addr] = buffers[addr].split(b'\n', 1)
                return message_complet.decode('utf-8')
    except BlockingIOError:
        # Pas encore assez de données reçues
        return None