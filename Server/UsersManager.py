import secrets
import threading
import time
from JSONDBFunctions import *

class UsersCollection:
    __instance = None
    TOKEN_SIZE = 16
    MAX_DISCONNECTED_TIME = 60 * 20 # en secondes ici 20
    TIME_BETWEEN_TOKEN_CHECK = 60 # en secondes ici 1 minute

    def __init__(self):
        self.__connected_users = {}
        self.__disconnected_users = {}
        self.__token_cleanup_thread = threading.Thread(target = self.__token_cleanup, args = (self,), daemon=True)
        self.__token_cleanup_thread.start()

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

    def __token_cleanup(self):
        while(True):
            time.sleep(self.TIME_BETWEEN_TOKEN_CHECK)
            current_time = time.time()
            expired_user_token = []
            for user in self.__disconnected_users:
                if(current_time - user["disconnectTime"] > self.MAX_DISCONNECTED_TIME):
                    expired_user_token.append(user)
            for user in expired_user_token:
                del self.disconnected_users[user]

    def __generate_token(self):
        return secrets.token_hex(self.TOKEN_SIZE)

    def connect_user(self, username):
        if(username in self.__connected_users):
            raise Exception("Utilisateur déjà dans la table des utilisateurs connectés")
        if(username in self.__disconnected_users):
            raise Exception("Utilisateur dans la table des utilisateurs déconnectés")
        token = self.__generate_token()
        self.__connected_users[username] = {"token":token}
        return token
    
    def disconnect_user(self, username):
        if(username not in self.connect_user):
            raise Exception("utilisateur pas dans la table des utilisateurs connectés")
        self.__disconnected_users[username] = {
            "token" : self.__connected_users[username],
            "disconnectTime" : time.time() 
            }
        del self.__connected_users[username]

    def reconnect_user(self, username):
        if(username not in self.__disconnected_users):
            raise Exception("Utilisateur absent de la table des utilisateurs déconnectés")

    def get_user_token(self, username):
        return self.__connected_users[username]["token"]
    
    def is_token_valid(self, token):
        for user in self.__disconnected_users:
            if(user["token"] == token):
                return True
        return False
    
class User():
    def __init__(self, username, token):
        self.tcp_sock = None
        self.username = username
        self.token = token

    def start_socket():
        pass

    def stop_socket():
        pass

