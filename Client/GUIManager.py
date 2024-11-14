import eel
import os
import json
import socket

TOKEN_PATH = "token.json"
UDPSOCK = None

def startGUI():
    tokenData = load_token()

    eel.init("UI")

    if(tokenData == False):
        eel.start("ConnectFrame.html")
    else:
        response = try_to_reconnect(tokenData)
        if(response["message"] == "inGame"):
            #TODO init TCP socket and get game data
            eel.start("Game.html")
            #TODO call JS func to send game data to GUI
            return
        if(response["message"] == "inMenu"):
            #TODO init TCP socket and get server list
            eel.start("RoomBrowser.html")
            #TODO call JS func to send server list to GUI
            return
        print(f"{response["message"]}")
        os.remove(TOKEN_PATH) # on delete le token dépassé
        eel.start("ConnectFrame.html")
        

def try_to_reconnect(tokenData):
    initUDPSocket()
    
    tokenData = load_token()
    token = tokenData["token"]
    server_address = tokenData["servAddr"]
    server_port = tokenData["port"]

    query = {
        "type" : "reconnect",
        "data" : {
            "token" : token
        }
    }

    query_str = json.dumps(query)

    UDPSOCK.sendto(query_str.encode(), (server_address, int(server_port)))
    print(f"message : {query} sent to {(server_address, int(server_port))}")
    responseRaw = UDPSOCK.recv(1024).decode()
    return json.loads(responseRaw)


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


def save_token(token, servAddr, port):
    print(f"token = {token}")
    


    with open(TOKEN_PATH, 'w', encoding='UTF-8') as file:
        dataJson = {"token": token, "servAddr": servAddr, "port": int(port)}
        
        json.dump(dataJson, file, indent=4)


def initUDPSocket():
    global UDPSOCK
    if UDPSOCK == None:
       UDPSOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


@eel.expose()
def connect_to_server(username, password, server_address, server_port):
    global UDPSOCK

    initUDPSocket()

    query = {
        "type" : "login",
        "data" : {
            "username" : username,
            "password" : password
        }
    }
    
    query_str = json.dumps(query) + "\n"

    UDPSOCK.sendto(query_str.encode(), (server_address, int(server_port)))
    print(f"message : {query} sent to {(server_address, int(server_port))}")
    responseRaw = UDPSOCK.recv(1024).decode()
    response = json.loads(responseRaw)

    print(f"reponse['message'] = {response["message"]}")
    save_token(response["message"], server_address, server_port)

    return json.loads(responseRaw)
    

@eel.expose()
def register_on_server(username, password, password_confirm, server_address, server_port:int):
    pass