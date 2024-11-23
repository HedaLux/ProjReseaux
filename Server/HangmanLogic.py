from HangmanWords import words, get_random_word

class Hangman():

    def __init__(self, players, nb_tries):
        self.word = get_random_word()
        self.players_state = {}
        self.nb_tries = nb_tries
        for player in players:
            self.players_state[player.token] = {
                'word': '_' * len(self.word),  # Mot masqué
                'nb_tries_left': nb_tries,    # Nombre d'essais restants
                #'guessed_letters': []         # Lettres devinées si nécessaire
            }

    def guess_letter(self, player_token, guess):

        if not self.__check_player_existence(player_token):
            raise Exception(f"Le joueur [{player_token}] n'a pas de gamestate")
        

        if self.players_state[player_token]["nb_tries_left"] == 0:
            return -1  # Pas d'essais restants

        # Si la lettre est correcte
        if guess in self.word:

            current_word = list(self.players_state[player_token]['word'])
            for index, letter in enumerate(self.word):
                if letter == guess:
                    current_word[index] = guess
            self.players_state[player_token]['word'] = ''.join(current_word)

 
            if self.players_state[player_token]['word'] == self.word:
                return 2  # Mot complété
            return 1  # Lettre correcte mais mot incomplet
        else:

            self.players_state[player_token]['nb_tries_left'] -= 1
            return 0  # Lettre incorrecte



    def add_player(self, player_token):
        if(self.__check_player_existence):
            raise Exception(f"le joueur [{player_token}] possède déjà un gamestate")
        self.players_state[player_token]['word'] = '_' * len(self.word)
        self.players_state[player_token]['nb_tries_left'] = self.nb_tries

    def get_player_gamestate(self, player_token):
        if(not self.__check_player_existence(player_token)):
            return None
        return self.players_state[player_token]
    
    def __check_player_existence(self, player_token):
        if(player_token in self.players_state):
            return True
        return False
