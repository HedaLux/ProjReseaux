import eel
import json
import Utils

@eel.expose
def guess_letter(letter):
    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "guessletter",
            "data": {
                "token": token,
                "letter": letter
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        print(f"Lettre envoyée : {letter}")

    except Exception as e:
        print(f"Erreur lors de l'envoi de la lettre : {str(e)}")

@eel.expose
def leave_room():
    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "leaveroom",
            "data": {
                "token": token
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        print("Requête de sortie de salle envoyée.")

    except Exception as e:
        print(f"Erreur lors de la sortie de la salle : {str(e)}")

@eel.expose
def request_game_state():
    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "gamestate",
            "data": {
                "token": token
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        print("Requête d'état du jeu envoyée.")

    except Exception as e:
        print(f"Erreur lors de la demande d'état du jeu : {str(e)}")


@eel.expose
def send_chat_message(message):
    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "sendchatmessage",
            "data": {
                "token": token,
                "message": message
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        print(f"Message de chat envoyé : {message}")

    except Exception as e:
        print(f"Erreur lors de l'envoi du message de chat : {str(e)}")


