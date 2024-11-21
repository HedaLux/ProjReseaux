import eel
import os
import json
import socket

TOKEN_PATH = "token.json"
UDPSOCK = None
TCP_SOCK = None

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
        print(f'{response["message"]}')
        os.remove(TOKEN_PATH) # on delete le token dépassé
        eel.start("ConnectFrame.html")
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
    with open(TOKEN_PATH, 'w', encoding='UTF-8') as file:
        dataJson = {"token": token, "servAddr": servAddr, "port": int(port)}
        
        json.dump(dataJson, file, indent=4)


def initUDPSocket():
    global UDPSOCK
    if UDPSOCK == None:
       UDPSOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

'''
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
    
    query_str = json.dumps(query) + '\n'

    UDPSOCK.sendto(query_str.encode(), (server_address, int(server_port)))
    print(f"message : {query} sent to {(server_address, int(server_port))}")
    response_raw = UDPSOCK.recv(1024).decode()
    response = json.loads(response_raw)

    print(f"reponse['message'] = {response['message']}")

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((server_address, response["message"]["port"]))

    save_token(response["message"]["token"], server_address, server_port)

    return json.loads(response_raw)
    '''

@eel.expose()
def connect_to_server(username, password, server_address, server_port):
    global UDPSOCK, current_user, TCP_SOCK

    try:
        # Initialisation du socket UDP
        initUDPSocket()

        # Création de la requête de connexion
        query = {
            "type": "login",
            "data": {
                "username": username,
                "password": password
            }
        }
        query_str = json.dumps(query) + '\n'

        # Envoi de la requête UDP
        UDPSOCK.sendto(query_str.encode(), (server_address, int(server_port)))
        print(f"Message envoyé : {query} à {(server_address, int(server_port))}")

        # Réception de la réponse du serveur
        response_raw = UDPSOCK.recv(1024).decode()
        response = json.loads(response_raw)

        # Affichage de la réponse pour débogage
        print(f"Réponse reçue : {response['message']}")

        if response.get("response") == "success":
            # Création de la connexion TCP
            TCP_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            TCP_SOCK.connect((server_address, response["message"]["port"]))

            # Sauvegarde du token utilisateur et mise à jour de l'utilisateur courant
            save_token(response["message"]["token"], server_address, server_port)
            current_user = username

            return response
        else:
            # En cas d'erreur dans la réponse
            return {"response": "error", "message": response.get("message", "Erreur inconnue")}
    except Exception as e:
        # Gestion des exceptions
        return {"response": "error", "message": str(e)}

    

@eel.expose()
def register_on_server(username, password, password_confirm, server_address, server_port:int):
    global UDPSOCK, TCP_SOCK, current_user

    try:
        initUDPSocket()

        query = {
            "type": "register",
            "data": {
                "username": username,
                "password": password,
                "passwordConfirm": password_confirm
            }
        }
        query_str = json.dumps(query) + '\n'

        # Envoi de la requête d'inscription
        UDPSOCK.sendto(query_str.encode(), (server_address, int(server_port)))

        response_raw = UDPSOCK.recv(1024).decode()
        response = json.loads(response_raw)


        if response.get("response") == "success":
            save_token(response["message"]["token"], server_address, server_port)
            # Après inscription, établir une connexion TCP 
            TCP_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(response)
            TCP_SOCK.connect((server_address, response["message"]["port"]))
            current_user = username
            print(f"Utilisateur {username} inscrit et connecté en TCP.")
            return {"response": "success", "message": f"Utilisateur {username} inscrit et connecté."}
        else:
            return {"response": "error", "message": response.get("message", "Erreur inconnue")}
    except Exception as e:
        return {"response": "error", "message": str(e)}



@eel.expose()
def get_user_stats_ui():
    global TCP_SOCK

    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "getuserstats",
            "data": {
                "token": token
            }
        }

        #verifier que le socket TCP est ouvert
        if TCP_SOCK is None:
            return {"response": "error", "message": "Connexion TCP non établie"}

        # Envoyer la requete des stats
        TCP_SOCK.sendall((json.dumps(query) + "\n").encode())

        response_raw = TCP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        if response.get("response") == "success":
            return {"response": "success", "stats": response.get("message")}
        else:
            return {"response": "error", "message": response.get("message", "Erreur inconnue")}
    except Exception as e:
        return {"response": "error", "message": str(e)}


@eel.expose
def create_room(room_data):
    global TCP_SOCK

    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "createroom",
            "data": {
                "token": token,
                "room": room_data
            }
        }

        # Envoi de la requête au serveur
        TCP_SOCK.sendall((json.dumps(query) + "\n").encode())

        # Réception de la réponse
        response_raw = TCP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        return response
    except Exception as e:
        return {"response": "error", "message": str(e)}


@eel.expose
def get_rooms():
    global TCP_SOCK

    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        # Construire la requête pour récupérer les salles
        query = {
            "type": "getrooms",
            "data": {
                "token": token
            }
        }

        # Envoyer la requête au serveur
        TCP_SOCK.sendall((json.dumps(query) + "\n").encode())

        # Réception de la réponse
        response_raw = TCP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        return response
    except Exception as e:
        return {"response": "error", "message": str(e)}







