import socket
import threading
import time
import json
from CORConnectionQueries import CORUDPQueriesWrapper as CORUDP, NoHandlerException


# 0.0.0.0 = toutes les interfaces réseau
SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345

def start_connection_process(stop_event):
    UDP_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDP_Socket.bind((SERVER_IP, SERVER_PORT))
    UDP_Socket.settimeout(5.0) # timeout de 5 secondes sur les lectures pour vérifier si le stop_event(fermeture de l'application) est set

    print(f"Serveur lancé sur {SERVER_IP}:{SERVER_PORT}")
    print("Serveur en attente de message.")

    while not stop_event.is_set():
        try:
            encoded_query, client_address = UDP_Socket.recvfrom(1024)

            print(f">> message reçu de <{client_address}> message = {encoded_query}")

            query = json.loads(encoded_query.decode()) #TODO rajouter un try except

            if("type" in query):
                try:
                    CORUDP.get_instance().handle(UDP_Socket, query, client_address)
                    print("requête traitée avec succès")
                    print("Serveur en attente de message.")
                except(NoHandlerException):
                    print(f"Le client [{client_address}] a envoyé une requête inconnue ({query["type"]})")
                    #TODO envoyer une erreur au client
            else:
                pass
                #TODO envoyer une erreur au client
        # Comme il y a un timeout de 5 secondes sur l'instruction recvfrom, il faut continuer à boucler tant que le stop_event n'est pas set        
        except socket.timeout:
            continue
            
    UDP_Socket.close()
    print("socket UDP fermé")


if __name__ == "__main__":
    stop_event = threading.Event() # évenement qui permet d'arrêter un thread lorsqu'il est .set() ici il sert pour arrêter le thread si l'application est fermée par l'utilisateur
    
    connection_thread_UDP = threading.Thread(target = start_connection_process, args=(stop_event,))
    connection_thread_UDP.start()
    
    try:
        while True:
            time.sleep(1)  # Boucle principale en attente d'un KeyboardInterrupt
    except KeyboardInterrupt:
        print("Interruption reçue, arrêt du serveur...")
        stop_event.set()  # Signaler au thread de s'arrêter

    connection_thread_UDP.join()
    print("le thread de connexion s'est fermé correctement")
    #TODO Start server here GUI
