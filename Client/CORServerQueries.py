from abc import ABC, abstractmethod

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
class GuessWordRes(QueryHandler):
    def handle(self, query):
        if(query["type"] != "guesswordres"):
            self._try_next(query)
            return


# Maillon lorsqu'on recoit un message
class MessageReceived(QueryHandler):
    def handle(self, query):
        if(query["type"] != "messagerecv"):
            self._try_next(query)
            return


# Maillon quand la salle change de status
class RoomStateChange(QueryHandler):
    def handle(self, query):
        if(query["type"] != "roomstatechange"):
            self._try_next(query)
            return


# Maillon quand on récupère les infos de la salle
class RoomInfo(QueryHandler):
    def handle(self, query):
        if(query["type"] != "roominfo"):
            self._try_next(query)
            return
        

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
        self.__head = LoginQuery()
        self.__head = RegisterQuery(self.__head)
        self.__head = LogoutQuery(self.__head)
        self.__head = ReconnectQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORServerQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORConnectionQueriesWrapper")
        return cls.__instance