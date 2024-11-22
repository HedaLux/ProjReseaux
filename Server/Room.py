import time
import secrets
import threading
import socket
from enum import Enum
from utils import Status
from Users import *
from CORHangmanQueries import *

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
        self.players[room_owner.token] = room_owner
        
        self.players[room_owner.token]["score"] = 0

        self.stop_event = threading.Event()
        self.handle_message_thread = threading.Thread(target=self.handle_players_message)
        self.handle_message_thread.start()

        self.current_hangman = None

    def handle_players_message(self):
        while not self.stop_event.is_set():
            for player in self.players:
                if(not player.status == Status.INGAME):
                    pass
                if(not player.conn == None):
                    message = self.read_player_message(player)
                    CORHangmanQueriesWrapper.get_instance().handle(message)

    def read_player_message(self, player):
        try:
            return recevoir_message_room(player.conn, player.addr, self.room_id)
        except:
            pass


    def start_game(self, player):
        if(player != self.room_owner):
            pass #TODO erreur
        
        while(self.current_round <= self.round_count):
            # initialisation du jeu de pendu pour le round actuel
            self.current_hangman = Hangman()
            for player in self.players:
                Hangman.add_player(player)
            
            # la room change de status et on enclenche le timer du round
            self.room_status = RoomStatus.ROUND_ONGOING
            self.notify_users() # on prévient les utilisateurs que le round vient de commencer
            self.current_duration = self.round_duration
            while not self.current_duration == 0:
                time.sleep(1)
                self.current_duration -= 1
            
            # le round est fini on met à jour les scores et on change de round
            self.update_scores()
            self.current_round = self.current_round + 1

            # la room change de status et on enclenche le cooldown inter round
            self.room_status = RoomStatus.ROUND_COOLDOWN
            self.notify_users() # on prévient les utilisateurs que le cooldown vient de se lancer
            self.current_cooldown = self.round_cooldown
            while not self.current_cooldown == 0:
                time.sleep(1)
                self.current_cooldown -= 1

        self.room_status = RoomStatus.GAME_ENDED
        self.notify_users() # on prévient les utilisateurs que la partie est terminée
        self.game_end()

    def notify_players(self):
        for player in self.players:
            if(not player.conn == None):
                message = {
                    
                }
                player.conn.send()

    def run_round(self, stop_event):
        while not stop_event.is_set():
            try:
                # on ecoute sur tous les sockets client connectés
                pass
            except socket.timeout:
                continue

    def game_end(self):
        RoomsCollection.get_instance().delete_room(self.room_id)

    def addPlayer(self, player):
        if(player not in self.players):
            self.players[player.token] = player
            self.players[player.token]["score"] = 0

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
