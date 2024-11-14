import time
from enum import Enum

class RoomStatus(Enum):
    WAITING = 1
    ROUND_ONGOING = 2
    ROUND_COOLDOWN = 3
    GAME_ENDED = 4

class Room():
    def __init__(self, max_player, round_count, round_duration, round_cooldown, no_tries, room_owner):
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
        
        while(self.current_round < self.round_count):
            self.room_status = RoomStatus.ROUND_ONGOING
            time.sleep(self.round_duration)
            self.room_status = RoomStatus.ROUND_COOLDOWN
            time.sleep(self.round_cooldown)

        self.room_status = RoomStatus.GAME_ENDED

    def addPlayer(self, player):
        self.players.add(player)