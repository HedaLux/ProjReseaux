from abc import ABC, abstractmethod
import socket
import threading
import secrets
import utils
from Users import *

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

        if("data" not in query):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect")
            return
        if("username" not in query["data"]):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect")
            return
        if("password" not in query["data"]):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect")
            return
        
        username = query["data"]["username"]
        password = query["data"]["password"]

        if not check_user_credentials(username, password):
            print(f"erreur la combinaison n'est pas dans la basse de données")
            utils.send_message_to(sock, client_address, "error", "nom d'utilisateur ou mot de passe incorrect")
            return
        
        token = UsersCollection.get_instance().add_user(username, client_address)

        data = {"token": token, "port": UsersCollection.SOCKET_ROOM_BROWSER_PORT}

        utils.send_message_to(sock, client_address, "success", data)

      
# Maillon d'inscription
class RegisterQuery(QueryHandler):
    def handle(self, sock, query, client_address):
        if(query["type"] != "register"):
            self._try_next(sock, query, client_address)
            return
        
        if("data" not in query):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect")
            return
        if("username" not in query["data"]):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect (nom d'utilisateur manquant)")
            return
        if("password" not in query["data"]):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect (mot de passe manquant)")
            return
        if("passwordConfirm" not in query["data"]):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect (confirmation du mot de passe)")
            return

        username = query["data"]["username"]
        password = query["data"]["password"]
        password_confirm = query["data"]["passwordConfirm"]


        if not check_username_disponibility(username):
            utils.send_message_to(sock, client_address, "error", "le nom d'utilisateur est déjà utilisé")
            return

        if not password == password_confirm:
            utils.send_message_to(sock, client_address, "error", "les 2 champs mot de passe ne correspondent pas")
            return


        add_user(query["data"]["username"], query["data"]["password"])
        
        token = UsersCollection.get_instance().add_user(username, client_address)
        response_data = {
            "token": token,  # Le token généré pour l'utilisateur
            "port": UsersCollection.SOCKET_ROOM_BROWSER_PORT  # Remplacez `tcp_port` par le port réellement utilisé pour la connexion TCP
        }

        utils.send_message_to(sock, client_address, "success", response_data)



# Maillon de déconnexion
class LogoutQuery(QueryHandler):
    def handle(self, sock, query, client_address):
        if(query["type"] != "logout"):
            self._try_next(sock, query, client_address)
            return
        
        #TODO supprimer l'utilisateur dans la classe singleton Users


# Maillon de reconnexion     
class ReconnectQuery(QueryHandler):
    def handle(self, sock, query, client_address):
        if(query["type"] != "reconnect"):
            self._try_next(sock, query, client_address)
            return
        
        if("data" not in query):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect")
            return
        if("token" not in query["data"]):
            utils.send_message_to(sock, client_address, "error", "la requête fournit est incorrect")
            return

        token = query["data"]["token"]
        
        if not UsersCollection.get_instance().is_token_valid(token):
            utils.send_message_to(sock, client_address, "error", "le token est dépassé ou incorrect")
            return
        
        utils.send_message_to(sock, client_address, "success", "inMenu") #TODO c'est temporaire il faut vérifier l'état dans lequel est l'utilisateur

        #TODO vérifier que le token est présent dans la classe singleton Users
        #TODO si non envoyer la réponse d'erreur
        #TODO si oui reconnecter l'utilisateur avec la classe singleton Users
        #TODO si oui envoyer la réponse de succès



# Classe singleton qui permet de construire une seule fois la chaine de responsabilité
class CORConnectionQueriesWrapper():
    __instance = None
    __head = None
    
    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = CORConnectionQueriesWrapper()
        return cls.__instance

    # utilisation => CORConnectionQueriesWrapper.get_instance().handle(params)
    # peut retourner un NoHandlerException si le type de requête est inconnu
    def handle(self, sock, query, client_address):
        self.__head.handle(sock, query, client_address)

    def __init__(self):
        self.__head = LoginQuery()
        self.__head = RegisterQuery(self.__head)
        self.__head = LogoutQuery(self.__head)
        self.__head = ReconnectQuery(self.__head)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(CORConnectionQueriesWrapper, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de CORConnectionQueriesWrapper")
        return cls.__instance