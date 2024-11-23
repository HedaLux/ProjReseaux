from abc import ABC, abstractmethod
from HangmanLogic import Hangman
import utils
import json

def notify_all_players_in_room(room, message_type, data):
    #import Room
    for player in room.players.values():
        if player.conn is not None:
            try:
                message = {
                    "type": message_type,
                    "data": data
                }
                player.conn.sendall(json.dumps(message).encode())
            except Exception as e:
                print(f"Erreur d'envoi au joueur {player.username}: {e}")


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


        if not token:
            utils.send_message_to(sock, client_address, "error", "Token ou ID de salle manquant")
            return

        from Room import RoomsCollection

        # Récupération de la salle
        room = RoomsCollection.get_instance().get_room_by_user(token)
        if not room:
            utils.send_message_to(sock, client_address, "error", f"Salle avec ID {room.room_id} introuvable")
            return

        # Vérification que le joueur est bien le propriétaire
        player = room.players.get(token)
        if not player:
            utils.send_message_to(sock, client_address, "error", f"Joueur avec token {token} non trouvé dans la salle")
            return

        if player != room.room_owner:
            utils.send_message_to(sock, client_address, "error", "Seul le propriétaire de la salle peut démarrer la partie")
            return

        # Démarrage de la partie
        try:
            print("room.start_game(player)")
            room.start_game(player)
            utils.send_message_to(sock, client_address, "success", "La partie a commencé")
        except Exception as e:
            utils.send_message_to(sock, client_address, "error", f"Erreur lors du démarrage de la partie : {str(e)}")

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
        self.__head = StartGameQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORHangmanQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORHangmanQueriesWrapper")
        return cls.__instance
