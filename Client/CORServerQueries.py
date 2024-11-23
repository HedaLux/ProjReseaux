from abc import ABC, abstractmethod

import eel

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


# Maillon quand un joueur quitte la salle
class UserLeftRoom(QueryHandler):
    def handle(self, query):
        if(query["type"] != "userleave"):
            self._try_next(query)
            return


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
class MessageReceived(QueryHandler):
    def handle(self, query):
        if(query["type"] != "messagerecv"):
            self._try_next(query)
            return


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
            eel.roundCooldown(query['data'].get("round_number", 1), query["data"].get("room_cooldown", 0))
        elif query['data']['status'] == 'ROUND_ONGOING':
            eel.roundStart(
                query['data'].get("round_number", 1),
                query['data'].get("word", "_ _ _ _"),
                query["data"].get("room_round_duration", 0)
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
        self.__head = MessageReceived(self.__head)
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