import socket
import threading
from game_logic import HangmanGame
from utils import handle_message, send_message

HOST = '127.0.0.1' #adresse loopback, ma machine uniquement, safe et conventionnel
PORT = 65432 #port libre et normalement disponible, possible de le changer en restant dans la bonne plage

games = {}  # Dictionnaire pour gérer plusieurs parties
clients_in_game = {}  # Mapping client -> salle de jeu

def broadcast_to_players(game_id, message):
    for client in games[game_id]['players']:
        send_message(client, message)

def client_handler(conn, addr):
    print(f"Client connecté : {addr}")
    
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
        # Cherche une salle avec un joueur déjà présent
        game_id = None
        for gid, game_data in games.items():
            if len(game_data['players']) == 1:  # Si une salle a déjà un joueur
                game_id = gid
                break

        # Si aucune salle n'existe ou si elles sont toutes pleines, créer une nouvelle salle
        if game_id is None:
            game_id = f"game_{len(games) + 1}"
            games[game_id] = {'game': HangmanGame(), 'players': [conn]}
            send_message(conn, {'message': 'En attente d\'un autre joueur pour commencer...'})
            print(f"Le client {addr} a été assigné à la nouvelle salle {game_id}.")
        else:
            # Si une salle incomplète a été trouvée, ajouter le joueur
            games[game_id]['players'].append(conn)
            print(f"Le client {addr} a rejoint la salle {game_id}.")
        
        #Voir ici plus haut pour limiter a 2 ? 
        
        clients_in_game[conn] = game_id

        # NE COMMENCE PAS LA PARTIE AVANT QUE 2 JOUEURS SOIENT PRÉSENTS
        if len(games[game_id]['players']) < 2:
        # Ne fais rien d'autre, attends que le deuxième joueur rejoigne
            return
        
            # Une fois que la salle est complète (2 joueurs)
        if len(games[game_id]['players']) == 2:
            broadcast_to_players(game_id, {'message': 'Le jeu commence !'})
            #broadcast_to_players(game_id, games[game_id]['game'].get_game_state())
            
            # Démarrer la boucle du jeu une fois que les 2 joueurs sont présents
            while not games[game_id]['game'].is_game_over():
                try:
                    # Tour de chaque joueur
                    for player in games[game_id]['players']:
                        send_message(player, {'message': 'C\'est votre tour !'})
                        send_message(player, games[game_id]['game'].get_game_state())
                        message = handle_message(player)
                        if message['action'] == 'guess':
                            games[game_id]['game'].guess_letter(message['letter'])
                            broadcast_to_players(game_id, games[game_id]['game'].get_game_state())
                        elif message['action'] == 'quit':
                            print(f"Le client {addr} a quitté la partie.")
                            break
                except ConnectionResetError:
                    print(f"Le client {addr} s'est déconnecté.")
                    break

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
