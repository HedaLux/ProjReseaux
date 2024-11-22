from abc import ABC, abstractmethod
#from UsersManager import UsersCollection
from Room import RoomsCollection
import utils
from JSONDBFunctions import get_user_stats
import json

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

        # Récupérer toutes les salles existantes
        rooms_collection = RoomsCollection.get_instance()
        rooms_data = []

        for room_id, room in rooms_collection.rooms.items():
            rooms_data.append({
                "room_id": room_id,
                "roomname": room.roomname,
                "owner": room.room_owner.username,
                "players": len(room.players),
                "max_players": room.max_player,
                "rounds": room.round_count,
                "status": room.room_status.name.lower()
            })

        # Envoyer les données au client
        utils.send_message_to(sock, client_address, "success", rooms_data)



class GetUserStatsQuery(RoomBrowserQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "getuserstats":
            self._try_next(sock, query, client_address)
            return

        #print("On est dans le maillon STATS \n")
        
        token = query["data"].get("token")
        from Users import UsersCollection
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
        from Users import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        room = RoomsCollection.get_instance().get_room(room_id)
        if room is None:
            utils.send_message_to(sock, client_address, "error", "Salle introuvable")
            return

        if len(room.players) >= int(room.max_player):
            utils.send_message_to(sock, client_address, "error", "Salle pleine")
            return

        room.addPlayer(user)
        utils.send_message_to(sock, client_address, "success", f"Connecté à la salle {room_id}")
        self.notify_all_players_in_room(
            room,
            "player_joined",
            {"username": user.username, "players": [p.username for p in room.players.values()]}
        )

    def notify_all_players_in_room(self, room, message_type, data):
    # Créez le message une fois au début
        message = {
            "type": message_type,
            "data": data
        }
        print(f"Message à envoyer à tous les joueurs dans la salle {room.roomname}: {message}\n")

        for player in room.players.values():
            if player.conn is not None:
                try:
                    # Envoi du message
                    print(f"Message à envoyer  {player.username}: {message}\n")
                    player.conn.sendall((json.dumps(message) + '\n').encode())
                except Exception as e:
                    print(f"Erreur d'envoi au joueur {player.username}: {e}")



# Maillon pour créer une salle
class CreateRoomQuery(RoomBrowserQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "createroom":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        room_data = query["data"].get("room")
        from Users import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        room_id = RoomsCollection.get_instance().new_room(
            roomname = room_data["roomname"],
            max_player=room_data["max_player"],
            round_count=room_data["round_count"],
            round_duration=room_data["round_duration"],
            round_cooldown=room_data["round_cooldown"],
            no_tries=room_data["no_tries"],
            room_owner=user
        )
        # Ajouter les informations complètes de la salle dans la réponse
        room = RoomsCollection.get_instance().get_room(room_id)
        room_info = {
            "room_id": room_id,
            "roomname": room.roomname,
            "owner": room.room_owner.username,
            "players": len(room.players),
            "max_players": room.max_player,
            "rounds": room.round_count,
            "status": room.room_status.name.lower()
        }

        utils.send_message_to(sock, client_address, "success", room_info)

class DisconnectQuery(RoomBrowserQueryHandler):
    def handle(self, sock, query, client_address):
        if query["type"] != "disconnect":
            self._try_next(sock, query, client_address)
            return

        token = query["data"].get("token")
        from Users import UsersCollection
        user = UsersCollection.get_instance().get_connected_user(token)

        if user is None:
            utils.send_message_to(sock, client_address, "error", "Utilisateur non connecté ou token invalide")
            return

        # Supprimer l'utilisateur des utilisateurs connectés
        UsersCollection.get_instance().remove_user(token)

        # Répondre avec succès
        utils.send_message_to(sock, client_address, "success", "Déconnexion réussie")



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
        self.__head = DisconnectQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORRoomBrowserQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORRoomBrowserQueriesWrapper")
        return cls.__instance
