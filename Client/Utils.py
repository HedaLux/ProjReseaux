import os
import socket
import json

TOKEN_PATH = "token.json"
UDPSOCK = None
TCP_SOCK = None

def load_token():
    if(os.path.exists(TOKEN_PATH)):
        with open(TOKEN_PATH, 'r', encoding='UTF-8') as file:
            data = json.load(file)
            if("token", "servAdrr", "port" in data):
                return data
            else:
                file.close()
                os.remove(TOKEN_PATH)
    return False

def initUDPSocket():
    global UDPSOCK
    if UDPSOCK == None:
       UDPSOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def save_token(token, servAddr, port):
    global TOKEN_PATH
    with open(TOKEN_PATH, 'w', encoding='UTF-8') as file:
        dataJson = {"token": token, "servAddr": servAddr, "port": int(port)}
        
        json.dump(dataJson, file, indent=4)

def close_UDP_sock():
    global UDPSOCK
    if not UDPSOCK == None:
        UDPSOCK.close()

def remove_token_file():
    try:
        os.remove("token.json")
        print("Fichier token.json supprimé.")
    except FileNotFoundError:
        print("Fichier token.json déjà supprimé.")