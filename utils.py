import json

def send_message(conn, message):
    conn.sendall((json.dumps(message) + '\n').encode())

def handle_message(conn):
    buffer = ''
    while True:
        data = conn.recv(1024).decode()  # Reçoit les données
        if not data:
            raise ConnectionResetError("La connexion a été interrompue")
        buffer += data
        if '\n' in buffer:  # Si un saut de ligne est trouvé, le message est complet
            message, buffer = buffer.split('\n', 1)  # Sépare le message complet du reste du buffer
            return json.loads(message)  # Retourne le message décodé