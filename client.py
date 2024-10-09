import socket
from utils import handle_message, send_message

HOST = '127.0.0.1'
PORT = 65432

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    try:
        while True:
            message = handle_message(client_socket)  # On reçoit le message du serveur
            if 'action' in message and message['action'] == 'choose_mode':
                print(message['message'])  # Demande de choisir le mode
                mode = int(input("Votre choix : "))
                send_message(client_socket, {'mode': mode})  # Envoi du mode choisi
            elif 'word' in message and 'tries_left' in message:
                print(f"État du jeu : {message['word']}, Essais restants : {message['tries_left']}")
                
                if message['status'] == 'win':
                    print("Félicitations, vous avez gagné !")
                    break
                elif message['status'] == 'lose':
                    print("Désolé, vous avez perdu.")
                    break

                # Proposer une lettre
                letter = input("Proposez une lettre : ")
                send_message(client_socket, {'action': 'guess', 'letter': letter})
            elif 'message' in message:
                print(f"Info serveur : {message['message']}")
            else:
                print(f"Message inattendu : {message}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()
