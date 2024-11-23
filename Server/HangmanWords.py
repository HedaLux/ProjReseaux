import random

#liste courte
words = [
    "arbre",
    "python",
    "appartement",
    "rouge"
]


#longue liste
'''words = [
    "arbre", "buisson", "feuille", "branche", "tronc", "racine", "herbe", "fleur", "rose", "tulipe",
    "lys", "marguerite", "chene", "sapin", "pin", "foret", "jungle", "savane", "plage", "ocean",
    "mer", "riviere", "lac", "cascade", "source", "rocher", "montagne", "colline", "falaise", "cratere",
    "volcan", "desert", "dune", "ile", "peninsule", "glacier", "grotte", "caverne", "prairie", "marais",
    "champ", "plaine", "pelouse", "jardin", "potager", "parc", "bosquet", "vegetation", "algue", "corail",
    "vent", "brise", "orage", "tonnerre", "eclair", "pluie", "neige", "grele", "tempete", "avalanche",
    "soleil", "lune", "etoile", "constellation", "galaxie", "univers", "planete", "satellite", "comete", "asteroide",
    "chat", "chien", "cheval", "vache", "mouton", "chevre", "cochon", "poulet", "canard", "oiseau",
    "aigle", "hibou", "chouette", "perroquet", "pingouin", "moineau", "pie", "cygne", "autruche", "dinde",
    "serpent", "lezard", "crocodile", "alligator", "tortue", "grenouille", "salamandre", "crapaud", "poisson", "requin",
    "baleine", "dauphin", "meduse", "pieuvre", "crabe", "homard", "crevette", "ours", "tigre", "lion",
    "zebre", "girafe", "rhinoceros", "elephant", "panthere", "loup", "renard", "singe", "gorille",
    "rat", "souris", "lapin", "lievre", "cerf", "biche", "herisson", "castor", "kangourou", "koala",
    "table", "chaise", "bureau", "lit", "armoire", "commode", "etagere", "tapis", "lampe", "ampoule",
    "rideau", "coussin", "oreiller", "couverture", "drap", "matelas", "miroir", "tableau", "horloge", "radio",
    "television", "ordinateur", "clavier", "souris", "ecran", "enceinte", "casque", "imprimante", "telephone", "camera",
    "refrigerateur", "four", "microondes", "grillepain", "lavevaisselle", "cafetiere", "bouilloire", "mixeur", "robot", "aspirateur",
    "voiture", "camion", "velo", "moto", "bus", "train", "avion", "bateau", "fussee", "helicoptere",
    "internet", "reseau", "routeur", "wifi", "logiciel", "algorithme", "donnees", "serveur", "programme",
    "application", "interface", "cloud", "fichier", "document", "tableur", "courrier", "email",
    "message", "cle", "disque", "lecteur", "stockage", "carte", "graphique", "processeur", "memoire", "systeme",
    "cybersecurite", "intelligence", "robot", "automatisation", "machine", "apprentissage", "big", "data",
    "modele", "simulation", "logiciel", "code", "script", "framework", "bibliotheque", "editeur", "compilateur",
    "pain", "baguette", "croissant", "brioche", "cereales", "pates", "riz", "quinoa", "ble", "mais",
    "chocolat", "fromage", "beurre", "creme", "yaourt", "lait", "viande", "poulet", "poisson",
    "saucisse", "jambon", "thon", "steak", "burger", "pizza", "quiche", "sandwich",
    "salade", "soupe", "ratatouille", "puree", "frite", "chips", "sauce", "ketchup", "mayonnaise", "moutarde",
    "fruit", "pomme", "poire", "banane", "orange", "citron", "ananas", "mangue", "fraise", "cerise",
    "peche", "abricot", "raisin", "pasteque", "melon", "kiwi", "figue", "prune", "noix", "amande",
    "rouge", "bleu", "vert", "jaune", "orange", "rose", "violet", "noir", "blanc", "gris",
    "marron", "turquoise", "beige", "cyan", "magenta", "ocre", "argent", "or", "bronze", "indigo",
    "medecin", "infirmier", "enseignant", "professeur", "pompier", "policier", "avocat", "juge", "ingenieur", "architecte",
    "journaliste", "ecrivain", "artiste", "peintre", "musicien", "compositeur", "chanteur", "acteur", "realisateur", "producteur",
    "agriculteur", "eleveur", "veterinaire", "boulanger", "boucher", "poissonnier", "pharmacien", "chimiste", "scientifique", "chercheur",
    "informaticien", "analyste", "consultant", "technicien", "mecanicien", "chauffeur", "plombier", "electricien", "menuisier", "ouvrier",
    "commercial", "vendeur", "banquier", "assureur", "courtier", "comptable", "gestionnaire", "directeur", "entrepreneur", "chef"
]'''


def get_random_word():
    if not words:
        raise Exception("La liste des mots est vide.")
    return random.choice(words)
