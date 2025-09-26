from shoe import Shoe
from player import Player, HumanStrategy, BasicStrategy, CardCountingPlayer
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
        self.max_bankrolls = {player: player.bankroll for player in self.players}

    
    def play_session(self):
        for player in self.players:
            if isinstance(player, CardCountingPlayer):
                player.card_counter = self.shoe.card_counter

        while True:
            if not self.players:
                if not self.interactive: print(f"No strategy made it {self.n_rounds} rounds!")

                self.print_bankroll_results()
                break
            result = Round(self.players, self.shoe, self.round_number, self.interactive).play_round()
            self.update_max_bankrolls()
            if result == "stop_session":
                # print("Debug: Human player is out of bankroll. Ending session.")

                self.print_bankroll_results()
                break
            self.round_number += 1
            if not self.interactive and self.round_number > self.n_rounds:
                
                self.print_bankroll_results()
                break
        
        # TODO
        # print results here, especially for sim, but I guess even if player is out of bankroll too
        # also need to keep track of game stats    

    def update_max_bankrolls(self) -> None:
        for player in self.max_bankrolls:
            if player.bankroll > self.max_bankrolls[player]:
                self.max_bankrolls[player] = player.bankroll


    def print_bankroll_results(self) -> None:
            print("\n", "=" * 30, sep="")
            print("\nBANKROLL RESULTS:")
            print("\n", "=" * 30, sep="")
            for player in self.max_bankrolls:
                max_bankroll = self.max_bankrolls[player]
                max_growth = ((max_bankroll - player.initial_bankroll) / player.initial_bankroll) * 100
                net_growth = ((player.bankroll - player.initial_bankroll) / player.initial_bankroll) * 100
                
                if max_growth.is_integer():
                    disp_max_g = str(int(max_growth))
                else:
                    disp_max_g = f"{max_growth:.2f}"

                if net_growth.is_integer():
                    disp_net_g = str(int(net_growth))
                else:
                    disp_net_g = f"{net_growth:.2f}"

                print(f"\n{player.name} finished with ${player.bankroll}")
                print(f"{player.name}'s max bankroll: ${max_bankroll}")
                print(f"Max bankroll growth: {disp_max_g}% Initial bankroll: ${player.initial_bankroll}")
                print(f"Net bankroll growth: {disp_net_g}%")
            print("")
