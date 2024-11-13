import eel
import os.path as osp
import json
import socket

TOKEN_PATH = "token.json"

def startGUI():
    token = get_token()

    eel.init("Client/UI")

    if(token == False):
        eel.start("ConnectFrame.html")
    else:
        response = try_to_reconnect(token)
        if(response["status"] == "inGame"):
            #TODO init TCP socket and get game data
            eel.start("Game.html")
            #TODO call JS func to send game data to GUI
            return
        if(response["status"] == "inMenu"):
            #TODO init TCP socket and get server list
            eel.start("MainMenu.html")
            #TODO call JS func to send server list to GUI
            return
        eel.start("ConnectFrame.html")
        #TODO delete the token file

def try_to_reconnect(token):
    pass

def get_token():
    if(osp.isfile(TOKEN_PATH)):
        with open(TOKEN_PATH, 'r+', encoding='UTF-8') as file:
            data = json.load(file)
            return data["token"]
    return False

def initUDPSocket():
    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return UDP_socket

@eel.expose()
def connect_to_server(username, password, server_address, server_port):
    UDP_socket = initUDPSocket()

    query = {
        "type" : "login",
        "data" : {
            "username" : username,
            "password" : password
        }
    }
    
    queryToString = json.dumps(query) + "\n"

    UDP_socket.sendto(queryToString.encode(), (server_address, int(server_port)))
    print(f"message : {query} sent to {(server_address, int(server_port))}")
    responseRaw = UDP_socket.recv(1024).decode()

    return json.loads(responseRaw)
    

@eel.expose()
def register_on_server(username, password, password_confirm, server_address, server_port:int):
    pass