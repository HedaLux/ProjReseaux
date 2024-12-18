import eel
import json
import Utils
import threading
import time
from CORServerQueries import CORServerQueriesWrapper

@eel.expose
def start_message_handling_thread():
    Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD_EVENT = threading.Event()
    Utils.TCP_SOCK.setblocking(False)
    Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD = threading.Thread(target=server_message_handler)
    Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD.start()

def server_message_handler():
    while not Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD_EVENT.is_set():
        time.sleep(0.1)
        message = read_message()
        if message:
            print(f"un nv message: {message}\n")
            messageJson = json.loads(message)
            CORServerQueriesWrapper.get_instance().handle(messageJson)
    Utils.TCP_SOCK.setblocking(True)

BUFFER = b""

def read_message():
    global BUFFER

    try:
        while True:
            data = Utils.TCP_SOCK.recv(1024)

            if not data:
                return None
            
            BUFFER += data
            # Vérifier si le séparateur '\n' est présent dans le buffer
            if b'\n' in BUFFER:
                message_complet, BUFFER = BUFFER.split(b'\n', 1)
                return message_complet.decode('utf-8')
            
            print(BUFFER)
    except BlockingIOError:
        # Pas encore assez de données reçues
        return None

@eel.expose
def guess_letter(letter):
    try:

        query = {
            "type": "guessletter",
            "data": {
                "token": Utils.TOKEN,
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

        query = {
            "type": "leaveroom",
            "data": {
                "token": Utils.TOKEN
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        Utils.HANGMAN_SERVER_MESSAGE_HANDLER_THREAD_EVENT.set()
        print("Requête de sortie de salle envoyée.")
        return 1

    except Exception as e:
        print(f"Erreur lors de la sortie de la salle : {str(e)}")
    
    return 0

@eel.expose
def request_game_state():
    try:

        query = {
            "type": "gamestate",
            "data": {
                "token": Utils.TOKEN
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        print("Requête d'état du jeu envoyée.")

    except Exception as e:
        print(f"Erreur lors de la demande d'état du jeu : {str(e)}")


@eel.expose
def send_chat_message(message):
    try:

        query = {
            "type": "sendchatmessage",
            "data": {
                "token": Utils.TOKEN,
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

        query = {
            "type": "startgame",
            "data": {
                "token": Utils.TOKEN
            }
        }

        Utils.TCP_SOCK.sendall((json.dumps(query) + "\n").encode())
        print("Hangman.py: Requête pour démarrer la partie envoyée.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la requête pour démarrer la partie : {str(e)}")
