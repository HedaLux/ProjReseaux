# A FAIRE
Quand on a perdu -> révéler le mot

# notes


# Suggestions
mode timer ? 
choix de la langue ? (fr/eng)
système de connection comme dans énoncé (UDP) (ip possible, compte preferable ?)
interface graphique ? 
ajouter BDD au serveur pour retenir pseudos ? scores, parties ?

--
multi: la victoire pose défaite (ou fin de partie en général)
Garder le tour quand on a juste





# Questions

1. Quel service est rendu par le serveur ?
Le serveur propose un jeu du pendu. Il choisit un mot aléatoirement et gère le déroulement de la partie, en envoyant les informations au client (état du mot, erreurs, victoires, etc.).

2. Que demande le client ?
Le client demande à jouer au jeu du pendu. Il envoie au serveur les lettres qu’il pense être dans le mot choisi.

3. Que répondra le serveur à la demande du client ?
Le serveur répond en indiquant :

Si la lettre proposée par le client est correcte ou non.
L’état actuel du mot avec les lettres devinées.
Le nombre d’essais restants.

4. Qu’est-ce qui est donc à la charge du serveur ?
Le serveur est responsable de :

Choisir le mot aléatoirement.
Maintenir l'état du jeu (mot, erreurs, lettres trouvées).
Communiquer avec le client et gérer les parties multiples (si mode concurrence).
Terminer la partie en cas de victoire, de défaite ou d'abandon du client.

5. Qui du serveur ou du client fixe les règles du jeu ?
Le serveur fixe les règles du jeu : nombre d’essais, structure du mot, gestion du chronomètre (si implémenté), etc.

6. Définir la structure et les champs d’un message envoyé par le client :
Voici une suggestion de structure pour les messages client :

Type de message (action de jeu, abandon, etc.)
Lettre proposée (si l’action est de deviner une lettre)
Identifiant joueur (pour les modes étendus comme multi-joueurs)
Numéro de partie (si plusieurs parties sont en cours)

7. Définir la structure et les champs d’un message envoyé par le serveur :
Le serveur pourrait envoyer :

Type de message (état du jeu, victoire, défaite)
État du mot (les lettres déjà devinées et les underscores pour les lettres restantes)
Nombre d’essais restants
Message de statut (indiquant victoire, défaite, ou lettre correcte/incorrecte)

8. Élaborer le séquencement des messages :
Le client envoie une requête pour commencer une partie.
Le serveur choisit un mot et envoie un message avec l’état initial du jeu (mot masqué).
Le client propose une lettre.
Le serveur répond avec l’état du mot après la proposition et le nombre d’essais restants.
Répétition jusqu’à la victoire ou la défaite.
Si le client abandonne, un message d’abandon est envoyé au serveur qui clôture la partie.

9. Diagrammes pour les différents scénarios :
Partie gagnée :

Client envoie une lettre.
Serveur informe que toutes les lettres ont été devinées.
Serveur envoie un message de victoire.

Partie perdue :

Client envoie une lettre incorrecte avec le dernier essai.
Serveur envoie un message de défaite.

Abandon :

Client envoie un message d’abandon.
Serveur clôture la partie et envoie une confirmation.



hangman/
│
├── server.py  # Serveur qui gère les connexions et le jeu du pendu
├── client.py  # Client qui se connecte au serveur et joue au jeu
├── game_logic.py  # Logique du jeu du pendu (séparation logique pour faciliter l'extensibilité)
├── utils.py  # Fonctions utilitaires pour la gestion des messages, etc.
└── README.md  # Instructions pour l'installation et l'exécution

MODE 2 : client vs client -> tout passe par le serveur qui fait la liasion
ROOMS ou salle de jeu -> pour la concurence
jeu via mot serveur 
-> amélioration ==> joueur choisis le mot? timer ? (points supplémentaires ou arret a la fin du timer) chat ? possibilité de demander un indice via perte de points ? système de points ? victoire sur plusieurs manches ? 
