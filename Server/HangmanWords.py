import random

words = [
    "python", "chat", "ordinateur", "lune", "pendu",
    "programmation", "musique", "voiture", "soleil", "montagne",
    "mer", "chocolat", "fromage", "village", "fleur",
    "livre", "camion", "commune"
    "papillon", "horloge", "oiseau", "lunettes", "tableau"
]

def get_random_word():
    if not words:
        raise Exception("La liste des mots est vide.")
    return random.choice(words)
