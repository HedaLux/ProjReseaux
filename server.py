import socket
import threading
from game_logic import HangmanGame
from utils import *
import time

HOST = '127.0.0.1'
PORT = 65432

games = {}  # Dictionnaire pour gérer plusieurs parties
clients_in_game = {}  # Mapping client -> salle de jeu
locks = {}  # Verrous pour chaque partie afin de synchroniser l'accès aux ressources partagées
game_threads = {}  # Mapping pour stocker les threads du gestionnaire de jeu

def broadcast_to_players(game_id, message):
    for client in games[game_id]['players']:
        send_message(client, message)

def game_manager(game_id):
    game = games[game_id]['game']
    players = games[game_id]['players']

    # Démarrer le jeu
    broadcast_to_players(game_id, {'message': 'Le jeu commence !'})
    
    while not game.is_game_over():
        current_player_index = games[game_id]['current_turn']
        current_player = players[current_player_index]

        # Informer tous les joueurs (sauf actuel) que ce n'est pas leur tour
        for player in players:
            if player != current_player:
                send_message(player, {'message': 'Ce n\'est pas ton tour, attends ton tour.'})

        # Envoyer un message uniquement au joueur dont c'est le tour
        send_message(current_player, {'message': 'C\'est votre tour !'})
        send_message(current_player, game.get_game_state())

        # Recevoir et traiter le message du joueur actuel
        try:
            message = handle_message(current_player)
            if message['action'] == 'guess':
                with locks[game_id]:  # Utiliser un verrou pour éviter les conflits d'accès
                    game.guess_letter(message['letter'])
                    #broadcast_to_players(game_id, game.get_game_state())
            elif message['action'] == 'quit':
                print(f"Le client s'est déconnecté.")
                break

            # Passer au joueur suivant
            games[game_id]['current_turn'] = (current_player_index + 1) % len(players)

        except ConnectionResetError:
            print(f"Le client s'est déconnecté.")
            break

    # Fin du jeu
    broadcast_to_players(game_id, {'message': 'Le jeu est terminé !'})

def client_handler(conn, addr):
    print(f"Client connecté : {addr}")

    while True:
        # Choisir un mode de jeu
        send_message(conn, {'action': 'choose_mode', 'message': 'Tapez 1 pour jouer contre le serveur, 2 pour joueur contre d\'autres joueurs'})
        mode = handle_message(conn)['mode']

        if mode == 1:
            # Mode joueur contre serveur
            game = HangmanGame()
            send_message(conn, game.get_game_state())
            while not game.is_game_over():
                try:
                    message = handle_message(conn)
                    if message['action'] == 'guess':
                        game.guess_letter(message['letter'])
                        send_message(conn, game.get_game_state())
                    elif message['action'] == 'quit':
                        print(f"Le client {addr} a quitté la partie.")
                        break
                except ConnectionResetError:
                    print(f"Le client {addr} s'est déconnecté.")
                    break

        elif mode == 2:
            # Mode joueur contre joueur
            game_id = None
            for gid, game_data in games.items():
                if len(game_data['players']) < 4:  # Limiter à 4 joueurs ou plus selon les besoins
                    game_id = gid
                    break

            if game_id is None:
                game_id = f"game_{len(games) + 1}"
                games[game_id] = {'game': HangmanGame(), 'players': [conn], 'current_turn': 0}
                clients_in_game[conn] = game_id
                locks[game_id] = threading.Lock()  # Créer un verrou pour cette partie
                send_message(conn, {'message': 'En attente d\'autres joueurs pour commencer...'})
                print(f"Le client {addr} a été assigné à la nouvelle salle {game_id}.")
            else:
                games[game_id]['players'].append(conn)
                clients_in_game[conn] = game_id
                print(f"Le client {addr} a rejoint la salle {game_id}.")

            # Si suffisamment de joueurs sont présents, démarrer le gestionnaire de jeu
            if len(games[game_id]['players']) == 2:  # Minimum de 2 joueurs pour commencer
                if game_id not in game_threads:  # Vérifier si le jeu n'a pas déjà démarré
                    thread = threading.Thread(target=game_manager, args=(game_id,))
                    game_threads[game_id] = thread
                    thread.start()

            # Attendre que le jeu se termine
            while not games[game_id]['game'].is_game_over():
                time.sleep(1)  

            send_message(conn, {'message': 'La partie est terminée. Merci d\'avoir joué !'})
            #break  # Sortir de la boucle lorsque la partie est terminée

    conn.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Serveur en écoute sur {HOST}:{PORT}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
