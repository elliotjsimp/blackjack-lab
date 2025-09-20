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
from collections import deque
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


# TODO: Replace hard-coded player.hands_collection[0]
class Player:
    def __init__(self, name: str, strategy: Strategy, bankroll: int=10000):
        self.name = name
        self.strategy = strategy
        self.bankroll = bankroll
        self.initial_bankroll = bankroll
        #self.current_bet: int = 0               # TODO: Refactor bet responsiblility to Hand.
        self.hands_collection: deque            # NOTE: Object gets replaced anyways in round.py at start of each round... could fix.
        self.current_hand: Hand                 # TODO: Change all methods (mainly make_decision() to use this)... might not be best though...
                                                # NOTE: Might need to make a hand : Move(s)/Result type of dict per player object
        self.final_hands: list[Hand]
        self.per_hand_result: dict[Hand: list[str]]

    def make_decision(self, dealer_upcard: Card) -> str:
        return self.strategy.make_decision(self, dealer_upcard)
    
    def make_bet(self) -> int:
        return self.strategy.make_bet(self)
    
    def valid_double(self) -> bool:
        return self.bankroll >= self.current_hand.bet * 2
    
    # FORMERLY: valid_split
    def can_split(self) -> bool:
        """Casino Convention: No more than 4 hands per round, per player."""
        return len(self.hands_collection) < 3 and self.valid_double() # Splitting effectively doubles your bet. Placeholder.
        # NOTE: Not checking if pair here. That is done on a per-hand basis. This is to see if the player can validly split.
        # This might not be the best design... it opens opportunity for errors I think.
    
    # TODO?: Some sort of method to loop through all player hands in hands_collection MAYBE...

    # NOTE: Some places use if self.interactive boolean flag, in round.py... can we replace? IDK.
    def is_human(self) -> bool:
        """Helper method to determine if a player is the human player."""
        return isinstance(self.strategy, HumanStrategy)
    
    def handle_bust(self) -> bool:
        """Do logic to handle when a Player busts a hand."""
        if self.current_hand.has_busted():
            # self.bankroll -= self.current_hand.bet # make sure not doubling...
            # self.current_hand.bet = 0 # might not need this line.
            self.per_hand_result[self.current_hand].append("bust")
            return True
        return False
    

    def record_cur_hand(self) -> None:
        self.final_hands.append(self.current_hand)

    
class Strategy(ABC):
    """Strategy is an abstract base class (inherited by every Player object)."""
    @abstractmethod
    def make_decision(self, player: Player, dealer_upcard: Card) -> str:
        pass

    @abstractmethod
    def make_bet(self, player: Player) -> int:
        pass


# --- Strategy Definitions ---

class RandomStrategy(Strategy):
    """Random choice (but stands at 21)."""
    def make_decision(self, player, dealer_upcard) -> str:
        return "stand" if player.current_hand.hand_total() == 21 else random.choice(["hit", "stand"])

    def make_bet(self, player) -> int:
        # Random bet between 10% and 25% of bankroll.
        return max(1, int(player.bankroll * random.uniform(0.1, 0.25) // 1))


class RationalStrategy(Strategy):
    """Follows dealer logic, stands at 17 or more."""
    def make_decision(self, player, dealer_upcard) -> str:
        if player.current_hand.hand_total() < 17:
            return "hit"
        return "stand"
    def make_bet(self, player) -> int:
        return max(1, int(player.bankroll * 0.05 // 1)) # Bets 5% of bankroll


class RationalOptimistStrategy(RationalStrategy):
    """Behaves like RationalStrategy but bets more aggressively."""
    def make_bet(self, player) -> int:
        # Bets 50% of bankroll
        return max(1, int(player.bankroll * 0.50 // 1))


class DoublerStrategy(Strategy):
    """Double instead of hit, every valid time."""
    def make_decision(self, player, dealer_upcard) -> str:
        if player.current_hand.hand_total() < 17:
            return "double" if player.valid_double() else "hit"
        return "stand"
    def make_bet(self, player) -> int:
        return max(1, int(player.bankroll * 0.20 // 1)) # Bets 20% of bankroll


class HumanStrategy(Strategy):
    """HumanStrategy... the fate of the game is left in your mortal hands! But forced to stand at 21."""
    def make_decision(self, player, dealer_upcard) -> str:
        if player.current_hand.hand_total() == 21: return "stand"   # Force stand by "dealer"
                                                                    # NOTE: Is this already handled in Round class?
        
        if player.valid_double():
            choices = ["hit", "h", "stand", "s", "double", "d"] # Did it this way because I was concerend about appending... I could fix probably.
            if player.can_split():
                choices.append("split")
        else:
            choices = ["hit", "h", "stand", "s"]

        
    
        return Manager.handle_input(
            message=f"Your hand: {player.current_hand.cards} (Score: {player.current_hand.hand_total()}), dealer shows {dealer_upcard}. Hit, stand or double? ",
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
        hand_total = player.current_hand.hand_total()

        # Commented out to handle after some sort of is pair determination.
        # if h_total >= 20: return "stand"
        # if h_total < 8: return "hit"

        dk = dealer_key(dealer_upcard)

        if player.current_hand.is_pair():
            pair_str = f"{dealer_key(player.current_hand.cards[0])}{dealer_key(player.current_hand.cards[1])}" # I guess could just do * 2.
            split_char = pair_splitting[pair_str][dk]
            decision_split = CHAR_TO_WORD[split_char]

            print(f"DEBUG: Decision to split: {decision_split} with {player.current_hand.cards} and DK: {dk}") 
            
            # We allow double after split. Takes away some house advantage.
            if decision_split in ["yes_split", "split_if_double_after_split"]:
                return "split"
            

        # If soft hand (could refactor to Hand class, when implemented).
        if any(c.rank == "A" for c in player.current_hand.cards) and len(player.current_hand.cards) == 2:

            # TODO: This entire block that essentially checks for if AA CAN BE REMOVED when split logic is implemented
            try: 
                other_card = next(c for c in player.current_hand.cards if c.rank != "A")
            except StopIteration:
                return "hit" # Always split on two aces, for now hit. Will remove this anyways.

            # Because the CSV is more readable as just short values (i.e., "H", "D")
            # But this looks bad in CLI.
            soft_total_repr = "A" + str(other_card.value)
            char = soft_totals[soft_total_repr][dk]
            return CHAR_TO_WORD[char]
        else:
            if hand_total <= 7: return "hit" # Already need to have determined if pair or not (using split/pair logic) for this to be sound.
            row_key = "17+" if hand_total >= 17 else str(hand_total)
            char = hard_totals[row_key][dk]
            return CHAR_TO_WORD[char]
        
    def make_bet(self, player):
        return max(1, int(player.bankroll * 0.001  // 1)) # Bets 0.1% of bankroll for now


class Players:
    # ROSTER = [
    #     Player("The Pro", BasicStrategy()),
    #     Player("Rational", RationalStrategy()),
    #     Player("Doubler", DoublerStrategy())
    # ]

    # Want to play alone with dealer.
    # ROSTER = []

    # Want to play with just The Pro, or simulate just The Pro.
    ROSTER = [
        Player("The Pro", BasicStrategy())
    ]

    #ROSTER.append(Player("Rational", RandomStrategy()))



    

