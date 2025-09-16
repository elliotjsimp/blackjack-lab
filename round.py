from player import Player, HumanStrategy, hand_total
from manager import Manager
from shoe import Shoe
from deck import Card


BANNER_LEN = 45 # amount of "=" that prints is multiplied by this constant (for per-round print methods)


class Round:
    """Defines a single Blackjack round."""

    def __init__(self, players: list[Player], shoe: Shoe, round_number: int, interactive: bool):
        self.players = players
        self.shoe = shoe
        self.round_number = round_number
        self.interactive = interactive
        self.dealer_hand: list[Card] = []

        # This is probably not best decision but fine for now...
        # Whatever is best for performance for large `n_rounds` in session (for data analysis) is what should probably be implemented in the future...
        self.decisions = {player: [] for player in self.players}

    def play_round(self):
        """Handles core round logic. I've tried to provide an ample amount of comments, mainly
        for people who may not know how Blackjack works."""

        # --- Removal Check ---
        for player in self.players[:]: # Create shallow copy so we can iterate and remove safely at same time
            if player.bankroll <= 0:
                print(f"\n{player.name} was removed from the game for having no bankroll left!")
                if isinstance(player.strategy, HumanStrategy): # Not designed for multiple humans, therefore quit
                    print(f"That means you, {player.name}... get your strategy down, then show everyone at the tables what you're made of!\n")
                    return "stop_session"
                self.players.remove(player)

        # --- Take Bets ---
        for player in self.players:
            player.current_bet = player.make_bet()
        
        self.print_bets()

        # --- Initial deal ---
        for player in self.players:
            player.hand = [self.shoe.deal_card(), self.shoe.deal_card()]
        self.dealer_hand = [self.shoe.deal_card(), self.shoe.deal_card()]

        self.print_initial_deal()

        # --- Check for natural Blackjack's (auto-win) ---
        dealer_total = hand_total(self.dealer_hand)
        for player in self.players:
            player_total = hand_total(player.hand)
            if player_total == 21:
                if dealer_total == 21:
                    # Push Blackjack 
                    # NOTE: might not be exact right Blackjack term, should ensure.
                    self.decisions[player].append("push blackjack")
                else:
                    # Blackjack, Player wins 1.5× bet
                    self.decisions[player].append("blackjack")
                    player.bankroll += int(1.5 * player.current_bet)
                player.current_bet = 0 # Round over for player

        # --- Player turns ---
        for player in self.players:
            # This works because human is always at last index of players/last "seat", therefore table is ready to print.
            # This is generally prefered by IRL card-counters (if they play at a table with other people, that is).
            if isinstance(player.strategy, HumanStrategy): self.print_table_moves()

            # TODO: Make bust method for DRY.
            while True:
                if player.current_bet > 0:
                    decision = player.make_decision(self.dealer_hand[0]) # Dealer upcard passed as argument
                    self.decisions[player].append(decision)

                    if decision in ["hit", "h"]:
                        player.hand.append(self.shoe.deal_card())

                        if hand_total(player.hand) > 21:
                            self.decisions[player].append("bust")

                            player.bankroll -= player.current_bet
                            player.current_bet = 0
                            break
                    elif decision in ["stand", "s"]:
                        break
                    elif decision in ["double", "d"]: # doubling in Blackjack is effectively double bet, then hit.
                        # NOTE: Valid doubling is handled by each Strategy instance now. Maybe not the best solution...
                        player.current_bet *= 2

                        if isinstance(player.strategy, HumanStrategy):
                            print(f"You doubled your bet to ${player.current_bet}...")

                        player.hand.append(self.shoe.deal_card())

                        if hand_total(player.hand) > 21:
                            self.decisions[player].append("bust")

                            player.bankroll -= player.current_bet
                            player.current_bet = 0
                            break

                else:
                    break   # For players in for loop who have hit Blackjack (push or not (tie with dealer or not))),
                            # The "dealer" (else break code) forces them to be rational in these cases, and not play.
                            # We could apend "stand" here, but would be messy in tables/data.


        # --- Dealer turn ---
        dealer_total = hand_total(self.dealer_hand) # TODO: Why calling twice? Messy. Fix. I guess need to though.

        # Casino Convention: most dealers stand at 17 (soft or hard).
        while dealer_total < 17:
            self.dealer_hand.append(self.shoe.deal_card())
            dealer_total = hand_total(self.dealer_hand)
            # if self.interactive: print(f"Dealer hits: {self.dealer_hand} (Total: {dealer_total})")

        
        if self.interactive: print(f"\nDealer's full hand: {self.dealer_hand} (Total: {hand_total(self.dealer_hand)})\n")

        # --- Resolve bets ---
        # NOTE: Technichally, we are more like finalizing bankroll adjustments.
        # Semantic difference, but it would be better perhaps if we directly modified
        # Player bankroll at start of round (when bet occurs).
        # Now, we are displaying "new" bankroll in print_bets method, but not actually changing until after round play.
        # Should probably just parody real-world.
        # I guess I just didn't want to subtract, then add back... but doesn't need to be operation-optimized like this.

        for player in self.players:
            player_total = hand_total(player.hand)
            if player.current_bet <= 0: # Overloaded logically. Implementation Debt.
                                        # Would be better if some sort of flag.
                
                # These are the cases where no current bet
                # Therefore could be be bust, blackjack, or push blackjack
                # Kind of managing Implementation Debt here :(

                if self.interactive:
                    match(self.decisions[player][-1]):
                        case "bust":
                            print(f"{player.name} busted! (Total: {player_total})") 
                        case "blackjack":
                            print(f"{player.name} got a Blackjack! They got a 3:2 return on their bet.")
                        case "push blackjack":
                            print(f"{player.name} and the Dealer both hit a Blackjack! That's quite rare.")

                continue

            elif dealer_total > 21 or player_total > dealer_total:
                player.bankroll += player.current_bet # Player wins
                result = "wins"
            elif player_total == dealer_total:
                result = "push"
            else:
                player.bankroll -= player.current_bet # Player loses
                result = "loses"

            # TODO: Implement table print method instead of this placeholder.
            # if self.interactive: print(f"{player.name} {result} ${player.current_bet} (Total: {player_total})")
            print(f"{player.name} {result} ${player.current_bet} (Total: {player_total})")

            player.current_bet = 0

        # --- Recycle shoe if using CSM ---
        self.shoe.csm_recycle()


    # Please forgive my non-DRY (wet, if you will) implementations of the following print methods:
    def print_bets(self) -> None:
        """"""
        if not self.interactive: return None
        Manager.show_spinner()
        print("\n","="*BANNER_LEN, sep="")
        print(f"Round {self.round_number} Bets")
        print("="*BANNER_LEN)
        print("\nPlayer     | Bet          | New Bankroll") 
        print("-----------+--------------+--------------")
        for player in self.players:
            print(f"{player.name:<10} | {f'${player.current_bet}':>12} | ${player.bankroll-player.current_bet}")


    def print_initial_deal(self) -> None:
        """Prints the initial deal table, with the dealer upcard."""
        if not self.interactive: return None
        Manager.show_spinner(0.8) # Slightly longer

        print("\n","="*BANNER_LEN, sep="")
        print("Initial Deal")
        print("="*BANNER_LEN)
        print(f"\nDealer Shows {self.dealer_hand[0]}") # Dealer upcard
        print("\nPlayer     | Hand              | Total") 
        print("-----------+-------------------+-------")

        for player in self.players:
            hand_str = ", ".join(str(card) for card in player.hand)
            print(f"{player.name:<10} | {hand_str:<17} | {hand_total(player.hand)}")

    
    # TODO: Normalize naming convention project-wide (move vs decision... which?)
    def print_table_moves(self) -> None:
        """Prints the turns of all other players in order. To be used before HumanStrategy needs to make decision.""" # TODO: Make docstring more clear LOL
        if not self.interactive: return None
        Manager.show_spinner(0.8) # Slightly longer

        if len(self.players) <= 1: return None # if only HumanStrategy in self.players (ROSTER is hardcoded right now though).
        print("\n","="*BANNER_LEN, sep="")
        print("Table Moves") # TODO: Need better, more Blackjack native, titles where applicable, like here.
        print("="*BANNER_LEN)
        # TODO: Make it so the table width expands if needed to accomodate a player's big hand. Therefore won't need to be so ugly-wide by default.
        print("\nPlayer     | Hand                      | Move(s)")
        print("-----------+---------------------------+---------")

        for player in self.players:
            hand_str = ", ".join(str(card) for card in player.hand)

            # `d` is each str in array of str's as the value of decisions dict, with Player object as key.
            decisions_str = ", ".join(d.upper() for d in self.decisions[player])

            # NOTE: I could not print STAND if that's the last dedecision in decision_str (because redundant)
            print(f"{player.name:<10} | {hand_str:<19}       | {decisions_str}")


    def print_round_results(self):
        raise NotImplementedError