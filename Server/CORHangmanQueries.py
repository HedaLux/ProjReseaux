from abc import ABC, abstractmethod
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
        from Users import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        from Room import RoomsCollection
        room = RoomsCollection.get_instance().get_room_by_user(token)
        if room is None or not isinstance(room.current_hangman, Hangman):
            utils.send_message_to(sock, client_address, "error", "Aucune partie en cours dans cette salle")
            return

        result = room.current_hangman.guess_letter(token, guess)

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
        from Users import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        from Room import RoomsCollection
        room = RoomsCollection.get_instance().get_room_by_user(token)
        if room is None or not isinstance(room.current_hangman, Hangman):
            utils.send_message_to(sock, client_address, "error", "Aucune partie en cours dans cette salle")
            return

        gamestate = room.current_hangman.get_player_gamestate(user.token)
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
        from Users import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        from Room import RoomsCollection
        room = RoomsCollection.get_instance().get_room_by_user(token)

        if room is None:
            utils.send_message_to(sock, client_address, "error", "Salle introuvable")
            return

        room.remove_player(user.token)
        #user.current_room = None
        utils.send_message_to(sock, client_address, "success", "Vous avez quitté la salle")


class ChatMessageQuery(HangmanQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "sendchatmessage":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        message = query["data"].get("message")

        from Users import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecte ou token invalide")
            return

        from Room import RoomsCollection
        room = RoomsCollection.get_instance().get_room_by_user(user.username)

        if room is None:
            utils.send_message_to(sock, client_address, "error", "L'utilisateur n'est pas dans une salle, message impossible")
            return

        # Diffuser le message à tous les joueurs de la salle (voir la mécanique du chat)
        for player in room.players:
            try:
                player_sock = UsersCollection.get_instance().get_connected_user_socket(player)
                chat_data = {
                    "type": "receivechatmessage",
                    "data": {
                        "sender": user.username,
                        "message": message
                    }
                }
                utils.send_message_to(player_sock, None, "success", chat_data)
            except Exception as e:
                print(f"Erreur lors de l'envoi du message à {player}: {str(e)}")


# Maillon pour commencer la partie
class StartGameQuery(HangmanQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "startgame":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        room_id = query["data"].get("room-id")

        from Room import RoomsCollection

        player = RoomsCollection.get_room(room_id).get_player(token)

        RoomsCollection.get_room(room_id).start_game(player)

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
        self.__head = ChatMessageQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORHangmanQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORHangmanQueriesWrapper")
        return cls.__instance
