import eel
import socket
import json
import Utils

@eel.expose()
def connect_to_server(username, password, server_address, server_port):

    try:
        # Initialisation du socket UDP
        Utils.initUDPSocket()

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
        Utils.UDP_SOCK.sendto(query_str.encode(), (server_address, int(server_port)))
        print(f"Message envoyé : {query} à {(server_address, int(server_port))}")

        # Réception de la réponse du serveur
        response_raw = Utils.UDP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        # Affichage de la réponse pour débogage
        print(f"Réponse reçue : {response['message']}")

        if response.get("response") == "success":
            # Création de la connexion TCP
            Utils.TCP_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Utils.TCP_SOCK.connect((server_address, response["message"]["port"]))

            # Sauvegarde du token utilisateur et mise à jour de l'utilisateur courant
            Utils.save_token(response["message"]["token"], server_address, server_port)
            current_user = username
            save_credentials(username, response["message"]["token"])
            return response
        else:
            # En cas d'erreur dans la réponse
            return {"response": "error", "message": response.get("message", "Erreur inconnue")}
    except Exception as e:
        # Gestion des exceptions
        return {"response": "error", "message": str(e)}
    
@eel.expose()
def register_on_server(username, password, password_confirm, server_address, server_port:int):

    try:
        Utils.initUDPSocket()

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
        Utils.UDP_SOCK.sendto(query_str.encode(), (server_address, int(server_port)))

        response_raw = Utils.UDP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)


        if response.get("response") == "success":
            Utils.save_token(response["message"]["token"], server_address, server_port)
            # Après inscription, établir une connexion TCP 
            Utils.TCP_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(response)
            Utils.TCP_SOCK.connect((server_address, response["message"]["port"]))
            save_credentials(username, response["message"]["token"])
            print(f"Utilisateur {username} inscrit et connecté en TCP.")
            return {"response": "success", "message": f"Utilisateur {username} inscrit et connecté."}
        else:
            return {"response": "error", "message": response.get("message", "Erreur inconnue")}
    except Exception as e:
        return {"response": "error", "message": str(e)}
    
def save_credentials(username, token):
    Utils.USERNAME = username
    Utils.TOKEN = token