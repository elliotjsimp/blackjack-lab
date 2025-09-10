from shoe import Shoe
from player import Player, HumanStrategy
from round import Round


class Session:
    """Defines an collection of rounds (a game)."""
    def __init__(self, players: list[Player], n_rounds: int=None):
        self.players = players
        self.shoe = Shoe()
        self.round_number = 1
        self.n_rounds = n_rounds
        # If any player is human, we consider this session interactive (needs print statements)
        self.interactive = any(isinstance(p.strategy, HumanStrategy) for p in players)
    
    def play_session(self):
        while True:
            if not self.players: 
                if not self.interactive: print(f"No strategy made it {self.n_rounds} rounds!")
                break
            result = Round(self.players, self.shoe, self.round_number, self.interactive).play_round()
            if result == "stop_session":
                # print("Debug: Human player is out of bankroll. Ending session.")
                break
            self.round_number += 1
            if not self.interactive and self.round_number > self.n_rounds:
                for p in self.players:
                    print(f"{p.name} finished with ${p.bankroll}")
                break
        
        # TODO
        # print results here, especially for sim, but I guess even if player is out of bankroll too
        # also need to keep track of game stats    

    


