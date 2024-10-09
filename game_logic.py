import random

WORDS = ['python', 'socket', 'network', 'dogs', 'stars', 'server']

class HangmanGame:
    def __init__(self):
        self.word = random.choice(WORDS)
        self.word_state = ['_' for _ in self.word]
        self.tries_left = 6     # Nombre d'essais, 6 pour un pendu classique
        self.guessed_letters = set()

    def guess_letter(self, letter):
        if letter in self.guessed_letters:
            return
        self.guessed_letters.add(letter)
        
        if letter in self.word:
            for i, char in enumerate(self.word):
                if char == letter:
                    self.word_state[i] = letter
        else:
            self.tries_left -= 1

    def is_game_over(self):
        return self.tries_left <= 0 or '_' not in self.word_state

    def get_game_state(self):
        return {
            'word': ''.join(self.word_state), # Le mot actuel, avec les lettres devinées
            'tries_left': self.tries_left,    # Nombre d'essais restants
            'status': self.get_status()       # statut du jeu 
        }

    def get_status(self):
        if '_' not in self.word_state:
            return 'win'
        elif self.tries_left <= 0:
            return 'lose'
        return 'ongoing'
