import time
import secrets
import threading
import socket
from enum import Enum
import utils
from Users import *
from CORHangmanQueries import *
import json

class RoomStatus(Enum):
    WAITING = 1
    ROUND_ONGOING = 2
    ROUND_COOLDOWN = 3
    GAME_ENDED = 4

class Room():
    def __init__(self, room_id, roomname, max_player, round_count, round_duration, round_cooldown, no_tries, room_owner):
        self.room_id = room_id
        self.roomname = roomname
        self.max_player = max_player
        self.round_count = round_count
        self.round_duration = round_duration
        self.current_duration = 0
        self.round_cooldown = round_cooldown
        self.current_cooldown = 0
        self.no_tries = no_tries
        self.room_owner = room_owner
        self.current_round = 1
        self.room_status = RoomStatus.WAITING
        self.players = {}
        self.players_score = {}

        self.players[room_owner.token] = room_owner
        self.players_score[room_owner.token] = 0

        self.stop_event = threading.Event()
        self.handle_message_thread = threading.Thread(target=self.handle_players_message)
        self.handle_message_thread.start()

        self.current_hangman = None

    def handle_players_message(self):
        if self.stop_event.is_set():
            print("stop event")
        while not self.stop_event.is_set():
            players_copy = list(self.players.values())
            time.sleep(0.1)
            for player in players_copy:
                if(not player.status == utils.Status.INGAME):
                    pass
                if(not player.conn == None):
                    message = self.read_player_message(player)

                    if message is None:
                        continue
                    print(f"Lecture du message pour le joueur {player.username}")
                    print("message handlePlayerMessages : ")
                    print(message)
                    print("\n")
                    query = json.loads(message)
                    CORHangmanQueriesWrapper.get_instance().handle(player.conn, query, player.addr)

    def read_player_message(self, player):
        try:
            return utils.recevoir_message_room(player.conn, player.addr, self.room_id)
        except:
            pass

    def start_game(self, player):
        if(player != self.room_owner):
            return #TODO erreur
        
        if(not self.room_status == RoomStatus.WAITING):
            return #TODO erreur

        thread_game_handler = threading.Thread(target=self.game_handler)
        thread_game_handler.start()

    def game_handler(self):
        while(self.current_round <= int(self.round_count)):
            # initialisation du jeu de pendu pour le round actuel
            self.current_hangman = Hangman(list(self.players.values()), self.no_tries)

            #appel redondant avec l'init de Hangman qui fait déja ça
            #for player in self.players.values():
                #self.current_hangman.add_player(player.token)

            
            # la room change de status et on enclenche le cooldown inter round
            self.room_status = RoomStatus.ROUND_COOLDOWN
            
            # le round est fini on met à jour les scores et on change de round
            #self.update_scores()
            self.current_round = self.current_round + 1

            self.notify_players() # on prévient les utilisateurs que le cooldown vient de se lancer
            self.current_cooldown = int(self.round_cooldown)
            while not self.current_cooldown == 0:
                time.sleep(1)
                self.current_cooldown -= 1
                print(f"timer of the cooldown : {self.current_cooldown}")

            # la room change de status et on enclenche le timer du round
            self.room_status = RoomStatus.ROUND_ONGOING   
            self.notify_players() # on prévient les utilisateurs que le round vient de commencer
            self.current_duration = int(self.round_duration)
            while not self.current_duration == 0:
                time.sleep(1)
                self.current_duration -= 1
                print(f"timer of the room : {self.current_duration}")

        self.room_status = RoomStatus.GAME_ENDED
        self.notify_players() # on prévient les utilisateurs que la partie est terminée
        print("zoulou\n\n")
        self.game_end()

    def notify_players(self):
        for player in self.players.values():  # Parcourir les objets joueurs, pas les clés
            if player.conn is not None:  # Vérifiez que conn n'est pas None
                message = {
                    "type": "status_change",
                    "data": {
                        "status": self.room_status.name
                    }
                }

                try:
                    player.conn.sendall((json.dumps(message) + "\n").encode())
                except Exception as e:
                    print(f"Erreur lors de l'envoi d'un message au joueur {player.token}: {e}")


    def game_end(self):
        RoomsCollection.get_instance().delete_room(self.room_id)

    def addPlayer(self, player):
        if(player not in self.players):
            self.players[player.token] = player
            self.players_score[player.token] = 0

    def remove_player(self, player_token):
        if player_token in self.players:
            del self.players[player_token]
            print(f"Le joueur avec le token {player_token} a été retiré de la salle {self.room_id}")
        else:
            print(f"Le joueur avec le token {player_token} n'est pas dans la salle {self.room_id}")

        if not self.players:
            print(f"La salle {self.room_id} est vide. Suppression en cours.")
            RoomsCollection.get_instance().delete_room(self.room_id)



"""
CONTENEUR DES ROOMS : classe singleton
"""
class RoomsCollection():
    ROOM_ID_SIZE = 16
    __instance = None

    def __init__(self):
        self.rooms = {}

    def __new__(cls, *args, **kwargs):
        # Si l'instance n'existe pas encore, on en crée une
        if cls.__instance is None:
            cls.__instance = super(RoomsCollection, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de RoomsCollection")
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = RoomsCollection()
        return cls.__instance

    def new_room(self, roomname, max_player, round_count, round_duration, round_cooldown, no_tries, room_owner):
        room_id = secrets.token_hex(self.ROOM_ID_SIZE)
        room = Room(room_id, roomname, max_player, round_count, round_duration, round_cooldown, no_tries, room_owner)
        self.rooms[room_id] = room
        return room_id

    def delete_room(self, room_id):
        if(room_id not in self.rooms):
            raise Exception(f"la room [{room_id}] n'existe pas")
        self.rooms.popitem(room_id)

    def get_room(self, room_id):
        if(room_id not in self.rooms):
            return None
        return self.rooms[room_id]
    
    def get_room_by_user(self, user_token):
        for room in self.rooms.values():
            if user_token in room.players:
                return room
        return None

