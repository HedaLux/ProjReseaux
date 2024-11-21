import eel
import os
import json
from ConnectFrameFunc import *
from RoomBrowser import *
from Hangman import *
from Utils import *


def startGUI():
    tokenData = load_token()

    eel.init("UI")

    if(tokenData == False):
        eel.start("ConnectFrame.html", port=0)
    else:
        response = try_to_reconnect(tokenData)
        if(response["message"] == "inGame"):
            #TODO init TCP socket and get game data
            eel.start("Game.html", port=0)
            #TODO call JS func to send game data to GUI
            return
        if(response["message"] == "inMenu"):
            #TODO init TCP socket and get server list
            eel.start("RoomBrowser.html", port=0)
            #TODO call JS func to send server list to GUI
            return
        print(f'{response["message"]}')
        os.remove(TOKEN_PATH) # on delete le token dépassé
        eel.start("ConnectFrame.html", port=0)
        eel.notify_token_failure(response["message"])
        

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

    try:
        UDPSOCK.sendto(query_str.encode(), (server_address, int(server_port)))
    except:
        pass
    
    print(f"message : {query} sent to {(server_address, int(server_port))}")
    responseRaw = UDPSOCK.recv(1024).decode()
    return json.loads(responseRaw)