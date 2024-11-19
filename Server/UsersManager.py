import secrets
import threading
import time
import socket
from utils import *
from JSONDBFunctions import *

class UsersCollection:
    __instance = None
    TOKEN_SIZE = 16
    MAX_DISCONNECTED_TIME = 60 * 20 # en secondes ici 20
    TIME_BETWEEN_TOKEN_CHECK = 60 # en secondes ici 1 minute
    SOCKET_ROOM_BROWSER_PORT = 25001
    SOCKET_ROOM_BROWSER_QUEUE = 25

    def __init__(self):
        self.__connected_users = {}
        self.__disconnected_users = {}
        self.__token_cleanup_thread = threading.Thread(target = self.__token_cleanup, daemon=True)
        self.__token_cleanup_thread.start()
        self.__socket_room_browser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket_room_browser.setblocking(0) 
        self.__socket_room_browser.bind(("0.0.0.0", self.SOCKET_ROOM_BROWSER_PORT))
        self.__socket_room_browser.listen(self.SOCKET_ROOM_BROWSER_QUEUE)
        self.__room_browser_thread = threading.Thread(target=self.__handle_room_browser)
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

    def __handle_room_browser(self):
        while(True):
            try:
                conn, addr = self.__socket_room_browser.accept()
                print(addr)
                conn.setblocking(False)
                for user in self.__connected_users:
                    if user.addr == addr:
                        user.conn = conn
                conn.close()
            except BlockingIOError:
                pass
            
            for user in self.__connected_users.values():
                try:
                    if not user.conn == None:
                        message = recevoir_message(self.__socket_room_browser, user.addr)
                        if message:
                            pass
                            #TODO handle message
                except (ConnectionResetError, ConnectionAbortedError):
                    self.disconnect_user(user)


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
    


    """def connect_user(self, username):
        if(username in self.__connected_users):
            raise Exception("Utilisateur déjà dans la table des utilisateurs connectés")
        if(username in self.__disconnected_users):
            raise Exception("Utilisateur dans la table des utilisateurs déconnectés")
        token = self.__generate_token()
        self.__connected_users[username] = {"token":token}
        return token"""
    
    def connect_user(self, username, addr):
        print(addr)
        token = self.__generate_token()
        user = User(username, token, addr)
        print(user.addr)
        
        self.__connected_users[token] = user
        return token
    
    def disconnect_user(self, user):
        self.__connected_users.popitem(user.token)
        self.__disconnected_users[user.token] = user

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

    def __init__(self, username, token, addr):
        self.conn = None
        self.addr = addr
        self.username = username
        self.token = token

    def start_connection(self):
        conn, addr = UsersCollection.get_instance().__socket_room_browser.accept()
        self.conn = conn
        self.addr = addr

    def stop_connection(self):
        self.conn = None
        self.addr = None

