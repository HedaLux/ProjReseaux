from abc import ABC, abstractmethod
from UsersManager import UsersCollection
from Room import RoomsCollection
from HangmanLogic import Hangman
import utils

# Exception si aucun maillon ne peut traiter la requête
class NoHandlerException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# Classe abstraite pour la chaîne de responsabilité
class HangmanQueryHandler(ABC):
    def __init__(self, successor=None):
        self.successor = successor

    @abstractmethod
    def handle(self, sock, query, client_address):
        pass

    def _try_next(self, sock, query, client_address):
        if self.successor is None:
            raise NoHandlerException("requête de type inconnu")
        self.successor.handle(sock, query, client_address)


# Maillon pour deviner une lettre
class GuessLetterQuery(HangmanQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "guessletter":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        guess = query["data"].get("letter")
        user = UsersCollection.get_instance().__connected_users.get(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        room_id = user.current_room
        room = RoomsCollection.get_instance().get_room(room_id)
        if room is None or not isinstance(room.game, Hangman):
            utils.send_message_to(sock, client_address, "error", "Aucune partie en cours dans cette salle")
            return

        result = room.game.guess_letter(user.token, guess)

        if result == -1:
            utils.send_message_to(sock, client_address, "error", "Vous n'avez plus d'essais restants")
        elif result == 1:
            utils.send_message_to(sock, client_address, "success", "Félicitations, vous avez gagné !")
        else:
            utils.send_message_to(sock, client_address, "success", "Lettre reçu par le serveur")


# Maillon pour récupérer l'état du jeu
class GameStateQuery(HangmanQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "gamestate":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        user = UsersCollection.get_instance().__connected_users.get(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        room_id = user.current_room
        room = RoomsCollection.get_instance().get_room(room_id)
        if room is None or not isinstance(room.game, Hangman):
            utils.send_message_to(sock, client_address, "error", "Aucune partie en cours dans cette salle")
            return

        gamestate = room.game.get_player_gamestate(user.token)
        if gamestate is None:
            utils.send_message_to(sock, client_address, "error", "État du jeu introuvable pour ce joueur")
        else:
            utils.send_message_to(sock, client_address, "success", gamestate)


# Maillon pour quitter la salle
class LeaveRoomQuery(HangmanQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "leaveroom":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        user = UsersCollection.get_instance().__connected_users.get(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        room_id = user.current_room
        room = RoomsCollection.get_instance().get_room(room_id)

        if room is None:
            utils.send_message_to(sock, client_address, "error", "Salle introuvable")
            return

        room.remove_player(user.token)
        user.current_room = None
        utils.send_message_to(sock, client_address, "success", f"Vous avez quitté la salle {room_id}")


# Classe singleton pour construire la chaîne de responsabilité
class CORHangmanQueriesWrapper:
    __instance = None
    __head = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = CORHangmanQueriesWrapper()
        return cls.__instance

    def handle(self, sock, query, client_address):
        self.__head.handle(sock, query, client_address)

    def __init__(self):
        self.__head = GuessLetterQuery()
        self.__head = GameStateQuery(self.__head)
        self.__head = LeaveRoomQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORHangmanQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORHangmanQueriesWrapper")
        return cls.__instance
