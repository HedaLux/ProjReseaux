import json
import hashlib
import secrets
import threading
import time

DB_FILENAME = 'users.json'
SALT = "7}3!=.qlTkUe"

class Users:
    __instance = None
    TOKEN_SIZE = 16
    MAX_DISCONNECTED_TIME = 60 * 20 # en secondes ici 20
    TIME_BETWEEN_TOKEN_CHECK = 60 # en secondes ici 1 minute

    def __init__(self):
        self.__connected_users = {}
        self.__disconnected_users = {}
        self.__token_cleanup_thread = threading.Thread(target = self.__token_cleanup, args = (self,), daemon=True)

    def __new__(cls, *args, **kwargs):
        # Si l'instance n'existe pas encore, on en crée une
        if cls.__instance is None:
            cls.__instance = super(Users, cls).__new__(cls)
        else:
            raise Exception("Impossible de créer une nouvelle instance de MaClasse")
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = Users()
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

def read_json(filename):
    with open(filename, 'r+', encoding='UTF-8') as file:
        data = json.load(file)
        return data


def write_json(filename, data):
    with open(filename, 'w+', encoding='UTF-8') as file:
        json.dump(data, file, indent=4)


def check_user_credentials(username, password):
    global DB_FILENAME
    
    user_DB = read_json(DB_FILENAME)
    
    to_hash = username + password + SALT
    hash = hashlib.sha256()
    hash.update(to_hash.encode('utf-8'))
    password_hash = hash.hexdigest()

    if username not in user_DB :
        return False
    if user_DB[username]['password'] != password_hash:
        return False
    return True


def check_username_disponibility(username):
    global DB_FILENAME
    
    user_DB = read_json(DB_FILENAME)
    if username in user_DB:
        return False
    return True


def add_user(username, password):
    global DB_FILENAME
    
    user_DB = read_json(DB_FILENAME)
    
    to_hash = username + password + SALT
    hash = hashlib.sha256()
    hash.update(to_hash.encode('utf-8'))
    password_hash = hash.hexdigest()
    
    if(check_username_disponibility(username)):
        user_DB[username] = {"password": password_hash}
        write_json(DB_FILENAME, user_DB)
        return True
    return False


def change_password(username, old_password, password, password_confirm):
    if(password != password_confirm):
        pass

    user_DB = read_json(DB_FILENAME)

    if(username not in user_DB):
        pass
    
    to_hash = username + old_password + SALT
    hash = hashlib.sha256()
    hash.update(to_hash.encode('utf-8'))
    old_password_hash = hash.hexdigest()

    if(user_DB[username][password] != old_password_hash):
        pass

    to_hash = username + password + SALT
    hash.update(to_hash.encode('utf-8'))
    password_hash = hash.hexdigest()

    user_DB[username][password] = password_hash


if __name__ == "__main__":
    add_user("Aurélien", "123456789")
    add_user("Nicolas", "123456789")
    add_user("Alice", "123456")
    add_user("Bob", "abcdef")
    add_user("Charlie", "password")
    add_user("David", "letmein")
    add_user("Eva", "123abc")
    add_user("Frank", "qwerty")
    add_user("Grace", "111111")
    add_user("Hannah", "123123")
    add_user("Irene", "welcome")
    add_user("Jack", "12345")
    add_user("Kate", "sunshine")
    add_user("Leo", "monkey")
    add_user("Mia", "football")
    add_user("Noah", "12345678")
    add_user("Olivia", "azerty")
    add_user("Paul", "qazwsx")
    add_user("Quinn", "000000")
    add_user("Rachel", "letmein")
    add_user("Sam", "abc123")
    add_user("Tina", "iloveyou")
    add_user("Ursula", "123321")
    add_user("Victor", "trustno1")
    add_user("Wendy", "superman")
    add_user("Xander", "qwertyuiop")
    add_user("Yara", "pass123")
    add_user("Zoe", "password1")