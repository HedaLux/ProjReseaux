import time
import secrets
import threading
from enum import Enum

class RoomStatus(Enum):
    WAITING = 1
    ROUND_ONGOING = 2
    ROUND_COOLDOWN = 3
    GAME_ENDED = 4

class Room():
    def __init__(self, room_id, max_player, round_count, round_duration, round_cooldown, no_tries, room_owner):
        self.room_id = room_id
        self.max_player = max_player
        self.round_count = round_count
        self.round_duration = round_duration
        self.round_cooldown = round_cooldown
        self.no_tries = no_tries
        self.room_owner = room_owner
        self.current_round = 1
        self.room_status = RoomStatus.WAITING
        self.players = {}
        self.players.add(room_owner)

    def start_game(self, player):
        if(player != self.room_owner):
            pass #TODO erreur
        
        while(self.current_round <= self.round_count):
            self.room_status = RoomStatus.ROUND_ONGOING
            
            stop_event = threading.Event()
            round_thread = threading.Thread(target = self.run_round, args=(self, stop_event))
            round_thread.start()

            time.sleep(self.round_duration)

            stop_event.set()
            round_thread.join()
            
            self.current_round = self.current_round + 1

            self.room_status = RoomStatus.ROUND_COOLDOWN
            time.sleep(self.round_cooldown)

        self.room_status = RoomStatus.GAME_ENDED
        self.game_end()

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
        self.players.add(player)

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

    def new_room(self, max_player, round_count, round_duration, round_cooldown, no_tries, room_owner):
        room_id = secrets.token_hex(self.ROOM_ID_SIZE)
        room = Room(max_player, room_id, round_count, round_duration, round_cooldown, no_tries, room_owner)
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
