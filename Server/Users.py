import secrets
import threading
import time
import socket
from enum import Enum
from CORRoomBrowserQueries import CORRoomBrowserQueriesWrapper
from utils import *
from JSONDBFunctions import *

class UsersCollection:
    __instance = None
    TOKEN_SIZE = 16 # la taille des tokens générés
    MAX_DISCONNECTED_TIME = 60 * 20 # en secondes ici 20 minutes
    INTERVAL_BETWEEN_TOKEN_CHECK = 60 # en secondes ici 1 minute
    SOCKET_ROOM_BROWSER_PORT = 25001
    SOCKET_ROOM_BROWSER_QUEUE = 25

    def __init__(self):
        self.__connected_users = {} # Dictionnaire des utilisateurs connectés en TCP
        self.__disconnected_users = {} # Dictionnaire des utilisateurs qui ont interrompu la connexion
        self.__waiting_to_connect_users = {} # Dictionnaire des utilisateurs qui se sont log via le socket UDP de connexion dont on attend la connexion TCP
        
        # Thread qui met à jour le dictionnaire "__disconnected_users" quand des utilisateurs sont déconnectés depuis trop longtemps
        self.__token_cleanup_thread = threading.Thread(target = self.__token_cleanup, daemon=True)
        self.__token_cleanup_thread.start()
        
        # Socket TCP qui gère les requête de la vue RoomBrowser
        self.__socket_room_browser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket_room_browser.setblocking(0) 
        self.__socket_room_browser.bind(("0.0.0.0", self.SOCKET_ROOM_BROWSER_PORT))
        self.__socket_room_browser.listen(self.SOCKET_ROOM_BROWSER_QUEUE)
        
        # Thread qui gère l'acceptation des connexions utilisateurs sur le socket "__socket_room_browser"
        self.__room_browser_accept_thread = threading.Thread(target=self.__handle_room_browser_tcp_accept)
        self.__room_browser_accept_thread.start()

        # Thread qui lit les messages envoyé sur le socket "__socket_room_browser"
        self.__room_browser_thread = threading.Thread(target=self.__handle_room_browser_messages)
        self.__room_browser_thread.start()


    def __new__(cls, *args, **kwargs):
        # Si l'instance n'existe pas encore, on en crée une
        if cls.__instance is None:
            cls.__instance = super(UsersCollection, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de UserCollection")
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = UsersCollection()
        return cls.__instance
    
    def get_connected_user(self, token):
        return self.__connected_users.get(token)

    def __handle_room_browser_tcp_accept(self):
        while True:
            # On gère les nouvelles connexions
            try:
                conn, addr = self.__socket_room_browser.accept()
                
                has_been_attributed = False
                
                conn.setblocking(False)

                for user in self.__waiting_to_connect_users.values():
                    print(user.username + " attend la connection tcp \n")
                    if user.addr[0] == addr[0]:
                        user.addr = addr
                        user.conn = conn
                        self.__waiting_to_connect_users.pop(user.token)
                        self.__connected_users[user.token] = user
                        has_been_attributed = True
                        break
                
                if(not has_been_attributed):
                    print(user.username + " has not been attributed ! \n")
                    conn.close()
                else:
                    print(f"connected user = {self.__connected_users}")
                    print(f"waiting for user = {self.__waiting_to_connect_users}")
                    print(f"disconnected user = {self.__disconnected_users}")
            except BlockingIOError:
                pass

    def __handle_room_browser_messages(self):
        while True:
            # On lit les messages des utilisateurs connectés
            # Ajout d'une copie ici pour éviter d'itérer dans une liste qui change de dimension
            __connected_users_copy = self.__connected_users.copy()
            for user in __connected_users_copy.values():
                if(user.status == Status.INMENU):
                    try:
                        message = recevoir_message(user.conn, user.addr)
                        if message:
                            print(f"Message reçu de {user.username}: {message}")
                        if message:
                            # Décoder la requête JSON
                            query = json.loads(message)
                            CORRoomBrowserQueriesWrapper.get_instance().handle(user.conn, query, user.addr)
                            pass
                            #TODO handle message
                    except (ConnectionResetError, ConnectionAbortedError):
                        self.disconnect_user(user)


    def __token_cleanup(self):
        while(True):
            time.sleep(self.INTERVAL_BETWEEN_TOKEN_CHECK)
            current_time = time.time()
            expired_user_token = []
            for user in self.__disconnected_users:
                if(current_time - user["disconnectTime"] > self.MAX_DISCONNECTED_TIME):
                    expired_user_token.append(user)
            for user in expired_user_token:
                del self.disconnected_users[user]


    def __generate_token(self):
        return secrets.token_hex(self.TOKEN_SIZE)
    


    """def connect_user(self, username):
        if(username in self.__connected_users):
            raise Exception("Utilisateur déjà dans la table des utilisateurs connectés")
        if(username in self.__disconnected_users):
            raise Exception("Utilisateur dans la table des utilisateurs déconnectés")
        token = self.__generate_token()
        self.__connected_users[username] = {"token":token}
        return token"""
    
    def add_user(self, username, addr):
        # On génère un nouveau token pour l'utilisateur
        token = self.__generate_token()

        # On créé l'utilisateur
        user = User(username, token, addr)
        
        # On ajoute l'utilisateur dans la fil d'attente des connexions
        self.__waiting_to_connect_users[token] = user
        return token
    
    # fonction pour la déconnexion non naturelle (crash, exctinction du pc, ...)
    def disconnect_user(self, user):
        user.conn = None
        self.__connected_users.pop(user.token)
        self.__disconnected_users[user.token] = user

    # fonction pour la déconnexion totale via le bouton "se déconnecter"
    def remove_user(self, token):
        user = self.__connected_users.pop(token, None)  # Supprimer des utilisateurs connectés
        if not user:
            user = self.__disconnected_users.pop(token, None)  # Supprimer des utilisateurs déconnectés
        if user:
            print(f"Utilisateur {user.username} complètement supprimé.")
        else:
            print(f"Aucun utilisateur trouvé avec le token : {token}")


    """def reconnect_user(self, user):
        pass"""

    """def disconnect_user(self, username):
        if(username not in self.connect_user):
            raise Exception("utilisateur pas dans la table des utilisateurs connectés")
        self.__disconnected_users[username] = {
            "token" : self.__connected_users[username],
            "disconnectTime" : time.time() 
            }
        del self.__connected_users[username]"""

    def reconnect_user(self, user):
        if(user.token not in self.__disconnected_users):
            raise Exception("Utilisateur absent de la table des utilisateurs déconnectés")

    def get_user_token(self, username):
        # Vérifier dans les utilisateurs connectés
        if username in self.__connected_users:
            return self.__connected_users[username]["token"]
        
        # Vérifier dans les utilisateurs en attente de connexion
        if username in self.__waiting_to_connect_users:
            return self.__waiting_to_connect_users[username]["token"]
        
        # Vérifier dans les utilisateurs déconnectés
        if username in self.__disconnected_users:
            return self.__disconnected_users[username]["token"]
        
        # Si non trouvé, lever une exception
        raise KeyError(f"Utilisateur {username} introuvable dans toutes les listes.")

    
    def is_token_valid(self, token):
        for user in self.__disconnected_users:
            if(user["token"] == token):
                return True
        return False

class User():

    def __init__(self, username, token, addr):
        self.conn = None
        self.addr = addr
        self.username = username
        self.token = token
        self.status = Status.INMENU

    def start_connection(self):
        conn, addr = UsersCollection.get_instance().__socket_room_browser.accept()
        self.conn = conn
        self.addr = addr

    def stop_connection(self):
        self.conn = None
        self.addr = None

