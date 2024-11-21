import eel
import json
import os
import Utils

@eel.expose
def disconnect_user():

    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "disconnect",
            "data": {
                "token": token
            }
        }

        # Envoyer la requête de déconnexion au serveur
        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())

        # Réception de la réponse
        response_raw = Utils.TCP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        if response.get("response") == "success":
            print("Déconnexion réussie.")
            Utils.remove_token_file()  # Supprimer le fichier token.json
        else:
            print(f"Erreur lors de la déconnexion : {response['message']}")

        # Fermer le socket TCP
        Utils.TCP_SOCK.close()
        return response
    except Exception as e:
        return {"response": "error", "message": str(e)}


@eel.expose()
def get_user_stats_ui():

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
        if Utils.TCP_SOCK is None:
            return {"response": "error", "message": "Connexion TCP non établie"}

        # Envoyer la requete des stats
        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())

        response_raw = Utils.TCP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        if response.get("response") == "success":
            return {"response": "success", "stats": response.get("message")}
        else:
            return {"response": "error", "message": response.get("message", "Erreur inconnue")}
    except Exception as e:
        return {"response": "error", "message": str(e)}


@eel.expose
def create_room(room_data):

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
        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())

        # Réception de la réponse
        response_raw = TCP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        return response
    except Exception as e:
        return {"response": "error", "message": str(e)}


@eel.expose
def get_rooms():

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
        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())

        # Réception de la réponse
        response_raw = Utils.TCP_SOCK.recv(1024).decode()
        response = json.loads(response_raw)

        return response
    except Exception as e:
        return {"response": "error", "message": str(e)}