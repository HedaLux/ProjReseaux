from abc import ABC, abstractmethod

import eel
import Utils

# Exception si aucun maillon ne peut traiter la requête
class NoHandlerException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# Classe abstraite qui représente un maillon de la COR
class QueryHandler(ABC):
    def __init__(self, successor=None):
        self.successor = successor
    
    @abstractmethod
    def handle(self, query):
        pass

    def _try_next(self, query):
        if(self.successor == None):
            raise NoHandlerException("requête de type inconnu")
        self.successor.handle(query)


# Maillon quand un joueur rejoins la salle
class UserJoinedRoom(QueryHandler):
    def handle(self, query):
        if(query["type"] != "userjoin"):
            self._try_next(query)
            return
        
        username = query["data"]["username"]

        eel.userJoined(username)


# Maillon quand un joueur quitte la salle
class UserLeftRoom(QueryHandler):
    def handle(self, query):
        if(query["type"] != "userleft"):
            self._try_next(query)
            return
        
        username = query["data"]["username"]

        eel.userLeft(username)


# Maillon quand le serveur envoi la réponse à un guess
class GuessLetterResponse(QueryHandler):
    def handle(self, query):
        if query["type"] != "guessletterres":
            self._try_next(query)
            return

        letter = query["data"]["letter"]
        result = query["data"]["result"]
        word = query["data"]["word"]
        tries_left = query["data"]["tries_left"]

        # Appeler la fonction côté UI pour mettre à jour l'affichage
        eel.guessResult(letter, result, word, tries_left)



# Maillon lorsqu'on recoit un message
class ChatMessageReceived(QueryHandler):
    def handle(self, query):
        if query["type"] != "chat_message":
            self._try_next(query)
            return

        sender = query["data"]["sender"]
        message = query["data"]["message"]

        # Appelle la fonction existante dans JavaScript pour afficher le message
        eel.addMessageToTchat(message, sender)



# Maillon quand la salle change de status
class RoomStateChange(QueryHandler):
    def handle(self, query):
        if(query["type"] != "status_change"):
            self._try_next(query)
            return
    
        print(query)

        # Appeler les fonctions UI correspondantes via Eel
        # Faire en sorte que le message amene la data voulue

        if query['data']['status'] == 'ROUND_COOLDOWN':
            eel.roundCooldown(query['data'].get("round_number", 1))
        elif query['data']['status'] == 'ROUND_ONGOING':
            eel.roundStart(
                query['data'].get("round_number", 1),
                query['data'].get("word", "_ _ _ _")
            )
        elif query['data']['status'] == 'GAME_ENDED':
            eel.gameEnd()


# Maillon quand on récupère les infos de la salle
class RoomInfo(QueryHandler):
    def handle(self, query):
        if(query["type"] != "roominfo"):
            self._try_next(query)
            return
        
        print(query)

        gamestate = query["data"]["gamestate"]
        round_status = query["data"]["round_status"]
        round_count = query["data"]["round_count"]
        round_duration = query["data"]["round_duration"]
        round_cooldown = query["data"]["round_cooldown"]
        notries = query["data"]["notries"]
        room_owner = query["data"]["room_owner"]
        current_round = query["data"]["current_round"]
        current_round_cooldown = query["data"]["current_round_cooldown"]
        current_round_duration = query["data"]["current_round_duration"]
        player_list = query["data"]["player_list"]
        
        
        self.set_room_info(Utils.USERNAME, round_count, round_duration, round_cooldown, notries, room_owner, player_list)

        if(round_status == "ROUND_ONGOING"):
            pass

        if(round_status == "ROUND_COOLDOWN"):
            pass

        if(round_status == "GAME_ENDED"):
            pass



        """
        # Appeler les fonctions UI correspondantes via Eel
        # Faire en sorte que le message amene la data voulue
        if query['data']['status'] == 'ROUND_COOLDOWN':
            eel.roundCooldown(query['data'].get("round_number", 1), query["data"].get("room_cooldown", 0))
        elif query['data']['status'] == 'ROUND_ONGOING':
            eel.roundStart(
                query['data'].get("round_number", 1),
                query['data'].get("word", "_ _ _ _"),
                query["data"].get("room_round_duration", 0)
            )
        elif query['data']['status'] == 'GAME_ENDED':
            eel.gameEnd()
        """

    def set_room_info(self, username, round_count, round_duration, round_cooldown, notries, room_owner, player_list):
        eel.setRoomInfo(username, round_count, round_duration, round_cooldown, notries, room_owner, player_list)
        
class UpdatePlayerListQuery(QueryHandler):
    def handle(self, query):
        if query["type"] not in ["player_joined", "player_left"]:
            self._try_next(query)
            return


        players = query["data"]["players"]
        print("caba")
        eel.update_player_list(players)  # Fonction exposée côté JS pour mettre à jour l'interface



# Maillon pour valider les requêtes avant traitement
class ValidateQuery(QueryHandler):
    def handle(self, query):
        if "type" not in query:
            print(f"Message reçu ignoré par CORServerQueries : {query}")
            return  # Ignore le message
        self._try_next(query)


        

# Classe singleton qui permet de construire une seule fois la chaine de responsabilité
class CORServerQueriesWrapper():
    __instance = None
    __head = None
    
    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = CORServerQueriesWrapper()
        return cls.__instance

    # peut retourner un NoHandlerException si le type de requête est inconnu
    def handle(self, message):
        self.__head.handle(message)

    def __init__(self):
        self.__head = UserJoinedRoom()
        self.__head = UserLeftRoom(self.__head)
        self.__head = GuessLetterResponse(self.__head)
        self.__head = ChatMessageReceived(self.__head)
        self.__head = RoomStateChange(self.__head)
        self.__head = RoomInfo(self.__head)
        self.__head = UpdatePlayerListQuery(self.__head)
        self.__head = ValidateQuery(self.__head)
        print("COR ServerQueries initi \n")

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORServerQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORConnectionQueriesWrapper")
        return cls.__instance