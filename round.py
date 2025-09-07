from player import Player, HumanStrategy
from manager import Manager
from shoe import Shoe
from deck import Card, hand_total

BANNER_LEN = 40 # amount of "=" that prints is for per-round print methods is multiplied by this constant

class Round:
    """Defines a single Blackjack round."""
    

    def __init__(self, players: list[Player], shoe: Shoe, round_number: int, interactive: bool):
        self.players = players
        self.shoe = shoe
        self.round_number = round_number
        self.interactive = interactive
        self.dealer_hand: list[Card] = []

        # This is probably not best decision but fine for now...
        # Whatever is best for performance for large `n_rounds` in session (for data analysis) is what should be implemented in the future...
        self.decisions = {player: [] for player in self.players}

    def play_round(self):
        
        # --- Removal Check ---
        for player in self.players[:]:  # iterate over a shallow copy
            if player.bankroll <= 0:
                print(f"\n{player.name} was removed from the game for having no bankroll left!")
                if isinstance(player.strategy, HumanStrategy): # Not (yet?) designed for multiple humans
                    print(f"That means you, {player.name}... get your strategy down, then show everyone what you're made of!")
                    return "stop_session"
                self.players.remove(player)


        for player in self.players:
            player.current_bet = player.make_bet()
        
        # Not putting show_spinner calls in the associated function
        # Wanting in play_round for now.
        if self.interactive: 
            Manager.show_spinner()
            self.print_bets()

        # --- Initial deal ---
        for player in self.players:
            player.hand = [self.shoe.deal_card(), self.shoe.deal_card()]
        self.dealer_hand = [self.shoe.deal_card(), self.shoe.deal_card()]

        if self.interactive:
            Manager.show_spinner(1.0) # a bit more delay
            self.print_initial_deal()


        # --- Check for natural Blackjack's (auto-win) ---
        dealer_total = hand_total(self.dealer_hand)
        for player in self.players:
            player_total = hand_total(player.hand)
            if player_total == 21:
                if dealer_total == 21:
                    # Push Blackjack (wow!) (NOTE: might not be exact right term, should ensure)
                    self.decisions[player].append("push blackjack")
                else:
                    # Blackjack, Player wins 1.5× bet
                    self.decisions[player].append("blackjack")
                    player.bankroll += int(1.5 * player.current_bet)
                player.current_bet = 0 # Round over for player

        # --- Player turns ---
        for player in self.players:
            if isinstance(player.strategy, HumanStrategy):
                # double check... never know! (logicially equivalent statements)
                if self.interactive:
                    Manager.show_spinner(1.0) # a bit more delay
                    self.print_table_moves()

            while True:
                # if self.interactive: print(f"{player.name}'s hand: {player.hand} (Total: {hand_total(player.hand)})")

                if player.current_bet > 0:
                    decision = player.make_decision(self.dealer_hand[0]) # dealer upcard passed as argument
                    self.decisions[player].append(decision)

                    if decision == "hit":
                        player.hand.append(self.shoe.deal_card())

                        if hand_total(player.hand) > 21:
                            self.decisions[player].append("bust")

                            player.bankroll -= player.current_bet
                            player.current_bet = 0
                            break
                    elif decision == "stand":
                        break
                else:
                    break

        
        

        # --- Dealer turn ---
        if self.interactive: print(f"\nDealer's full hand: {self.dealer_hand} (Total: {hand_total(self.dealer_hand)})")
        dealer_total = hand_total(self.dealer_hand)
        
        # Casino convention: dealers stand at 17 (have different rules for if it's a soft 17 or not ("soft" == with an Ace))
        while dealer_total < 17:
            self.dealer_hand.append(self.shoe.deal_card())
            dealer_total = hand_total(self.dealer_hand)
            # if self.interactive: print(f"Dealer hits: {self.dealer_hand} (Total: {dealer_total})")
        
        # --- Resolve bets ---
        for player in self.players:
            if player.current_bet == 0:
                if self.interactive: print(f"{player.name} busted!")
                continue  # already busted
            player_total = hand_total(player.hand)
            if dealer_total > 21 or player_total > dealer_total:
                player.bankroll += player.current_bet  # player wins
                result = "wins"
            elif player_total == dealer_total:
                result = "push"
            else:
                player.bankroll -= player.current_bet  # player loses
                result = "loses"
            if self.interactive: print(f"{player.name} {result} (Dealer: {self.dealer_hand})")
            player.current_bet = 0

        # --- Recycle shoe if using CSM ---
        self.shoe.csm_recycle()


    # Please forgive my not DRY implementation of these print methods
    def print_bets(self):
        print("\n","="*BANNER_LEN, sep="")
        print(f"Round {self.round_number} Bets")
        print("="*BANNER_LEN)
        
        print("\nPlayer     | Bet    | Bankroll")
        print("-----------+--------+---------")
        for player in self.players:
            print(f"{player.name:<10} | {player.current_bet:>6} | {player.bankroll:>7}")


    def print_initial_deal(self):
        print("\n","="*BANNER_LEN, sep="")
        print("Initial Deal")
        print("="*BANNER_LEN)

        print(f"\nDealer Shows {self.dealer_hand[0]}")

        print("\nPlayer     | Hand              | Total") 
        print("-----------+-------------------+-------")

        for player in self.players:
            hand_str = ", ".join(str(card) for card in player.hand)
            print(f"{player.name:<10} | {hand_str:<17} | {hand_total(player.hand):<2}")
    
    # TODO: Normalize naming convention project-wide (move vs decision... which?)
    def print_table_moves(self):
        """Prints the turns of all other players in order. To be used before HumanStrategy needs to make decision.""" # TODO: Make docstring more clear LOL
        if len(self.players) <= 1: return None # if only HumanStrategy in self.players (ROSTER is hardcoded right now though).

        print("\n","="*BANNER_LEN, sep="")
        print("Table Moves") # TODO: Need better, more Blackjack native, titles where applicable, like here.
        print("="*BANNER_LEN)

        print("\nPlayer     | Hand              | Move(s)")
        print("-----------+-------------------+-------") # TODO: Adapt table width to what looks good for the result text

        # NOTE: This works because HumanStrategy Player (the user) is always at the last "seat" (index) of the players list
        # IRL Card-counters prefer this, or just playing 1-on-1 with the dealer.
        # Therefore, we might as well have user at last index, therefore this is fine.


        # NOTE: Shows table turns, not results. That will happen after
        # I guess will actually show BUST too...
        for player in self.players:

            # if isinstance(p.strategy, HumanStrategy): return None

            hand_str = ", ".join(str(card) for card in player.hand)
            # What will print for player decision(s) if natural Blackjack? What about if they reach 21?
            # Because I kind of force them to stop... but is that handled in strategy? I hope..
            # `decision` is each str in array as the value of decisions dict, with Player object as key.

            decisions_str = ", ".join(d.upper() for d in self.decisions[player]) # SHOW ALL
            # decisions_str = self.decisions[p][-1].upper() # SHOW LAST

            # NOTE: could not print STAND if that's the last one in decision_str (because redundant?)
            #if isinstance(plz)
            print(f"{player.name:<10} | {hand_str:<17} | {decisions_str}")


    def print_round_results(self):
        raise NotImplementedError