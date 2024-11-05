from abc import ABC, abstractmethod
import socket
import threading
import secrets
import utils
from UsersManager import check_user_credentials, check_username_disponibility, add_user

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
    def handle(self, sock, query, client_address):
        pass

    def _try_next(self, sock, query, client_address):
        if(self.successor == None):
            raise NoHandlerException("requête de type inconnu")
        self.successor.handle(sock, query, client_address)


# Maillon de connexion
class LoginQuery(QueryHandler):
    def handle(self, sock, query, client_address):
        if(query["type"] != "login"):
            self._try_next(sock, query, client_address)
            return

        if not check_user_credentials(query["data"]["username"], query["data"]["password"]):
            print(f"erreur la combinaison n'est pas dans la basse de données")
            #utils.send_error_message_to(sock, client_address, "nom d'utilisateur ou mot de passe incorrect")
            return
        
# Maillon d'insciption      
class RegisterQuery(QueryHandler):
    def handle(self, sock, query, client_address):
        if(query["type"] != "register"):
            self._try_next(sock, query, client_address)
            return
        
            
# Maillon de déconnexion
class LogoutQuery(QueryHandler):
    def handle(self, sock, query, client_address):
        if(query["type"] != "logout"):
            self._try_next(sock, query, client_address)
            return

# Maillon de reconnexion     
class ReconnectQuery(QueryHandler):
    def handle(self, sock, query, client_address):
        if(query["type"] != "reconnect"):
            self._try_next(sock, query, client_address)
            return



# Classe singleton qui permet de construire une seule fois la chaine de responsabilité
class CORUDPQueriesWrapper():
    _instance = None
    __head = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CORUDPQueriesWrapper()
        return cls._instance

    # utilisation => CORUDPQueriesWrapper.get_instance().handle(params)
    # peut retourner un NoHandlerException si le type de requête est inconnu
    def handle(self, sock, query, client_address):
        self.__head.handle(sock, query, client_address)

    def __init__(self):
        self.__head = LoginQuery()
        self.__head = RegisterQuery(self.__head)
        self.__head = LogoutQuery(self.__head)
        self.__head = ReconnectQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CORUDPQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORUDPQueriesWrapper")
        return cls._instance