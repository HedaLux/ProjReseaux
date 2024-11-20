from abc import ABC, abstractmethod
from UsersManager import *
from Room import RoomsCollection
import utils
from JSONDBFunctions import get_user_stats

# Exception si aucun maillon ne peut traiter la requête
class NoHandlerException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# Classe abstraite pour la chaîne de responsabilité
class RoomBrowserQueryHandler(ABC):
    def __init__(self, successor=None):
        self.successor = successor
    
    @abstractmethod
    def handle(self, sock, query, client_address):
        pass

    def _try_next(self, sock, query, client_address):
        if self.successor is None:
            raise NoHandlerException("requête de type inconnu")
        self.successor.handle(sock, query, client_address)


# Maillon pour récupérer la liste des salles
class GetRoomsQuery(RoomBrowserQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "getrooms":
            self._try_next(sock, query, client_address)
            return
        
        rooms = RoomsCollection.get_instance().rooms
        room_list = [{"room_id": room_id, "owner": room.room_owner, "players": len(room.players), "max_players": room.max_player} for room_id, room in rooms.items()]
        
        utils.send_message_to(sock, client_address, "success", room_list)


class GetUserStatsQuery(RoomBrowserQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "getuserstats":
            self._try_next(sock, query, client_address)
            return

        #print("On est dans le maillon STATS \n")
        
        token = query["data"].get("token")
        from UsersManager import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        try:
            # Récupération des stats à partir de JSONDBFunctions
            #print("Ici on try get_user_stats \n")
            stats = get_user_stats(user.username)
            #print(f"Les stats obtenues : {stats}\n")

            utils.send_message_to(sock, client_address, "success", stats)
        except Exception as e:
            utils.send_message_to(sock, client_address, "error", str(e))


# Maillon pour se connecter à une salle
class JoinRoomQuery(RoomBrowserQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "joinroom":
            self._try_next(sock, query, client_address)
            return

        room_id = query["data"].get("room_id")
        token = query["data"].get("token")
        user = UsersCollection.get_instance().__connected_users.get(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        room = RoomsCollection.get_instance().get_room(room_id)
        if room is None:
            utils.send_message_to(sock, client_address, "error", "Salle introuvable")
            return

        if len(room.players) >= room.max_player:
            utils.send_message_to(sock, client_address, "error", "Salle pleine")
            return

        room.addPlayer(user.username)
        utils.send_message_to(sock, client_address, "success", f"Connecté à la salle {room_id}")


# Maillon pour créer une salle
class CreateRoomQuery(RoomBrowserQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "createroom":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        room_data = query["data"].get("room")
        user = UsersCollection.get_instance().__connected_users.get(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        room_id = RoomsCollection.get_instance().new_room(
            max_player=room_data["max_player"],
            round_count=room_data["round_count"],
            round_duration=room_data["round_duration"],
            round_cooldown=room_data["round_cooldown"],
            no_tries=room_data["no_tries"],
            room_owner=user.username
        )
        utils.send_message_to(sock, client_address, "success", {"room_id": room_id})


# Classe singleton pour construire la chaîne de responsabilité
class CORRoomBrowserQueriesWrapper():
    __instance = None
    __head = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = CORRoomBrowserQueriesWrapper()
        return cls.__instance

    def handle(self, sock, query, client_address):
        self.__head.handle(sock, query, client_address)

    def __init__(self):
        self.__head = GetRoomsQuery()
        self.__head = GetUserStatsQuery(self.__head)
        self.__head = JoinRoomQuery(self.__head)
        self.__head = CreateRoomQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORRoomBrowserQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORRoomBrowserQueriesWrapper")
        return cls.__instance
