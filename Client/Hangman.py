import eel
import json
import Utils
import threading
import time
from CORServerQueries import CORServerQueriesWrapper

@eel.expose
def start_message_handling_thread():
    Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD_EVENT = threading.Event()
    Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD = threading.Thread(target=server_message_handler)
    Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD.start()

def server_message_handler():
    while not Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD_EVENT.is_set():
        message = read_message()
        messageJson = json.loads(message)
        CORServerQueriesWrapper.get_instance().handle(messageJson)
        time.sleep(0.1)

BUFFER = b""

def read_message():
    global BUFFER

    try:
        while True:
            data = Utils.TCP_SOCK.recv(1024)
            if not data and not BUFFER:
                return None
            BUFFER += data
            # Vérifier si le séparateur '\n' est présent dans le buffer
            if b'\n' in BUFFER:
                message_complet, BUFFER = BUFFER.split(b'\n', 1)
                return message_complet.decode('utf-8')
    except BlockingIOError:
        # Pas encore assez de données reçues
        return None

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
        Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD_EVENT.set()
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


@eel.expose
def start_game():
    try:
        with open("token.json", "r") as token_file:
            token_data = json.load(token_file)
            token = token_data["token"]

        query = {
            "type": "startgame",
            "data": {
                "token": token
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        print("Requête pour démarrer la partie envoyée.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la requête pour démarrer la partie : {str(e)}")
