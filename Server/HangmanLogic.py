from HangmanWords import words, get_random_word

class Hangman():

    def __init__(self, players, nb_tries):
        self.word = get_random_word()
        self.players_state = {}
        self.nb_tries = nb_tries
        for player in players:
            self.players_state[player.token]['word'] = '_' * len(self.word)
            self.players_state[player.token]['nb_tries_left'] = nb_tries

    def guess_letter(self, player_token, guess):
        if(not self.__check_player_existence(player_token)):
            raise Exception(f"le joueur [{player_token}] n'as pas de gamestate")
        
        if self.players_state[player_token]["nb_tries_left"] == 0:
            return -1
        
        if guess in self.word:
            for index, letter in enumerate(self.word):
                if letter == guess:
                    self.players_state[player_token]['word'][index] = guess
            
            if self.players_state[player_token]['word'] == self.word:
                return 1
        else:
            self.players_state[player_token]['nb_tries_left'] -= 1

        return 0

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
