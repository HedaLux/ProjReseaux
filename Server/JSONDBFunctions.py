import json
import hashlib

DB_FILENAME = 'users.json'
SALT = "7}3!=.qlTkUe"

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