from __future__ import annotations 
"""The above makes it so we can do Strategy class, 
then player class (or vice versa). We don't need 
to worry about not yet defined, or circular imports.
Basically asks Python to treat all type definitions 
in functions as strings until everything is defined)."""

import random
from manager import Manager
from deck import Card
from hand import Hand
from abc import ABC, abstractmethod
import csv


"""Used to convert from CSV move to game readable move (so printed tables don't have letters, 
even though they are valid for humans to type as moves for convenience)."""
CHAR_TO_WORD = {
    "H":"hit",
    "S":"stand",
    "D":"double",
    "Ds":"double",          # allowed to double is true, therefore double
    "Y": "yes_split",       # UNIMPLEMENTED
    "N": "no_split",        # UNIMPLEMENTED
    "Yn": "split_if_double_after_split" # UNIMPLEMENTED
}


def csv_to_dict(path: str, row_header_title: str) -> dict:
    d = {}
    with open(path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            key = row[row_header_title].strip()
            d[key] = {dealer.strip(): row[dealer].strip() for dealer in row if dealer != row_header_title}
        return d


# Dicts constructed using csv file paths
hard_totals = csv_to_dict("./tables/hard-totals.csv", "Player Total")
soft_totals = csv_to_dict("./tables/soft-totals.csv", "Player Total")
pair_splitting = csv_to_dict("./tables/pair-splitting.csv", "Player Pair") # NOTE: WIP.


def dealer_key(card: Card) -> str:
    """Returns the "dealer key" string value of a card. Used for csv value mapping."""
    if card.rank in ["J", "Q", "K"]:
        return "10"
    elif card.rank == "A":
        return "A"
    else:
        return card.rank



class Player:
    def __init__(self, name: str, strategy: Strategy, bankroll: int=1000):
        self.name = name
        self.strategy = strategy
        self.bankroll = bankroll
        self.current_bet: int = 0
        self.hand = Hand() # I think I need to have player hands, an array containing each hand (usually 1)

    def make_decision(self, dealer_upcard: Card) -> str:
        return self.strategy.make_decision(self, dealer_upcard)
    
    def make_bet(self) -> int:
        return self.strategy.make_bet(self)
    
    def valid_double(self) -> bool:
        return self.bankroll >= self.current_bet * 2
    
    
class Strategy(ABC):
    """Strategy is an abstract base class (inherited by every Player object)."""
    @abstractmethod
    def make_decision(self, player: Player, dealer_upcard: Card) -> str:
        pass

    @abstractmethod
    def make_bet(self, player: Player) -> str:
        pass


# --- Strategy Definitions ---

class RandomStrategy(Strategy):
    """Random choice (but stands at 21)."""
    def make_decision(self, player) -> str:
        return "stand" if player.hand.hand_total() == 21 else random.choice(["hit", "stand"])

    def make_bet(self, player) -> int:
        # Random bet between 10% and 25% of bankroll.
        return max(1, int(player.bankroll * random.uniform(0.1, 0.25) // 1))


class RationalStrategy(Strategy):
    """Follows dealer logic, stands at 17 or more."""
    def make_decision(self, player, dealer_upcard) -> str:
        if player.hand.hand_total() < 17:
            return "hit"
        return "stand"
    def make_bet(self, player) -> int:
        return max(1, int(player.bankroll * 0.20 // 1)) # Bets 20% of bankroll


class RationalOptimistStrategy(RationalStrategy):
    """Behaves like RationalStrategy but bets more aggressively."""
    def make_bet(self, player) -> int:
        # Bets 50% of bankroll
        return max(1, int(player.bankroll * 0.5 // 1))


class DoublerStrategy(Strategy):
    """Double instead of hit, every valid time."""
    def make_decision(self, player, dealer_upcard) -> str:
        if player.hand.hand_total() < 17:
            return "double" if player.valid_double() else "hit"
        return "stand"
    def make_bet(self, player) -> int:
        return max(1, int(player.bankroll * 0.20 // 1)) # Bets 20% of bankroll


class HumanStrategy(Strategy):
    """HumanStrategy... the fate of the game is left in your mortal hands! But forced to stand at 21."""
    def make_decision(self, player, dealer_upcard) -> str:
        if player.hand.hand_total() == 21: return "stand"    # Force stand by "dealer"
                                                            # NOTE: Is this already handled in Round class?
        
        if player.valid_double():
            choices = ["hit", "h", "stand", "s", "double", "d"] # Did it this way because I was concerend about appending... I could fix probably.
        else:
            choices = ["hit", "h", "stand", "s"]
    
        return Manager.handle_input(
            message=f"Your hand: {player.hand.cards} (Score: {player.hand.hand_total()}), dealer shows {dealer_upcard}. Hit, stand or double? ",
            choices=choices,
            input_type=str,
            invalid_message="That wasn't a valid play.")

    def make_bet(self, player) -> int:
        return Manager.handle_input(
            message=f"Your bankroll: ${player.bankroll}. Enter your bet amount: ",
            input_type=int,
            validator=lambda x: 0 < x <= player.bankroll,
            invalid_message="That wasn't a valid bet.")
    

class BasicStrategy(Strategy):
    """Note that "Basic Strategy" is a specific Blackjack strategy that makes the best move based on dealer upcard and their own hand total."""
    def make_decision(self, player, dealer_upcard) -> str:
        h_total = player.hand.hand_total()

        # Commented out to handle after some sort of is pair determination.
        # if h_total >= 20: return "stand"
        # if h_total < 8: return "hit"

        dk = dealer_key(dealer_upcard)

        if player.hand.is_pair():
            pair_str = f"{dealer_key(player.hand.cards[0])}{dealer_key(player.hand.cards[1])}" # I guess could just do * 2.
            split_char = pair_splitting[pair_str][dk]
            print(f"DEBUG: Decision to split: {CHAR_TO_WORD[split_char]} with {player.hand.cards} and DK: {dk}") 


        # If soft hand (could refactor to Hand class, when implemented).
        if any(c.rank == "A" for c in player.hand.cards) and len(player.hand.cards) == 2:

            # TODO: This entire block that essentially checks for if AA can be removed when split/pair logic is implemented.
            try: 
                other_card = next(c for c in player.hand.cards if c.rank != "A")
            except StopIteration:
                return "hit" # Always split on two aces, for now hit. Will remove this anyways.

            # Because the CSV is more readable as just short values (i.e., "H", "D")
            # But this looks bad in CLI.
            soft_total_repr = "A" + str(other_card.value)
            char = soft_totals[soft_total_repr][dk]
            return CHAR_TO_WORD[char]
        else:
            if h_total <= 7: return "hit" # Already need to have determined if pair or not (using split/pair logic) for this to be sound.
            row_key = "17+" if h_total >= 17 else str(h_total)
            char = hard_totals[row_key][dk]
            return CHAR_TO_WORD[char]
        
    def make_bet(self, player):
        return max(1, int(player.bankroll * 0.05 // 1)) # Bets 5% of bankroll for now


class Players:
    ROSTER = [
        Player("The Pro", BasicStrategy()),
        Player("Rational", RationalStrategy()),
        Player("Doubler", DoublerStrategy())
    ]

    # ROSTER = []

    # ROSTER = [
    #     Player("The Pro", BasicStrategy(), bankroll=1000),
    # ]



    

