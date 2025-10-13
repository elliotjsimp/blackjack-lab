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
from counter import CardCounter
from abc import ABC, abstractmethod
from collections import deque
import csv


"""Used to convert from CSV move to game readable move (so printed tables don't have letters, 
even though they are valid for humans to type as moves for convenience)."""
CHAR_TO_WORD = {
    "H":"hit",
    "S":"stand",
    "D":"double",
    "Ds":"double_if_possible_else_stand", # Double if possible, otherwise stand
    "Y": "yes_split",
    "N": "no_split",
    "Yn": "split_if_double_after_split"
}


def csv_to_dict(path: str, row_header_title: str) -> dict:
    d = {}
    with open(path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            key = row[row_header_title].strip()
            d[key] = {dealer.strip(): row[dealer].strip() for dealer in row if dealer != row_header_title}
        return d


# Dicts constructed from csv files. 
hard_totals = csv_to_dict("./tables/hard-totals.csv", "Player Total")
soft_totals = csv_to_dict("./tables/soft-totals.csv", "Player Total")
pair_splitting = csv_to_dict("./tables/pair-splitting.csv", "Player Pair")


def dealer_key(card: Card) -> str:
    """Returns the "dealer key" string value of a card. Used for csv value mapping."""
    if card.rank in ["J", "Q", "K"]:
        return "10"
    elif card.rank == "A":
        return "A"
    else:
        return card.rank


class Player:
    def __init__(self, name: str, strategy: Strategy, bankroll: int=50000):
        self.name = name
        self.strategy = strategy
        self.bankroll = bankroll
        self.initial_bankroll = bankroll
        self.hands_collection: deque # Constructed at the beginning of each round... Somewhat wasteful. Could fix.
        self.current_hand: Hand                 
        self.final_hands: list[Hand]
        self.per_hand_result: dict[Hand: list[str]]


    def make_decision(self, dealer_upcard: Card) -> str:
        return self.strategy.make_decision(self, dealer_upcard)
    

    def make_bet(self) -> int:
        return self.strategy.make_bet(self)
    

    # FORMERLY: valid_double
    def can_double(self) -> bool:
        """Return True if the player has enough bankroll to double their current bet."""
        return self.bankroll >= self.current_hand.bet # Fixed, was using bet * 2 still.
    
    
    # FORMERLY: valid_split
    def can_split(self) -> bool:
        """Casino Convention: No more than 4 hands per round, per player."""
        return len(self.hands_collection) < 4 and self.can_double() and self.current_hand.is_pair() # Splitting effectively doubles your bet.
        # NOTE: Now checking if pair also...
        # This might not be the best design... it opens opportunity for errors I feel.
    

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


class CardCountingPlayer(Player):
    def __init__(self, name: str, strategy: Strategy, bankroll: int=100000):
        super().__init__(name, strategy, bankroll)
        self.card_counter: CardCountingPlayer
    

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
            return "double" if player.can_double() else "hit"
        return "stand"
    def make_bet(self, player) -> int:
        return max(1, int(player.bankroll * 0.20 // 1)) # Bets 20% of bankroll


class HumanStrategy(Strategy):
    """HumanStrategy... the fate of the game is left in your mortal hands! But forced to stand at 21."""
    def make_decision(self, player, dealer_upcard) -> str:
        if player.current_hand.hand_total() == 21: return "stand"   # Force stand by "dealer"
                                                                    # NOTE: Is this already handled in Round class?
        
        choices = ["hit", "h", "stand", "s"]
        choice_indicator = "Hit or stand?"

        if player.can_double():
            choices.append("double")
            choices.append("d")
            choice_indicator = "Hit, double or stand?"
            if player.can_split():
                choices.append("split")
                choice_indicator = "Hit, double, split or stand?"


        return Manager.handle_input(
            message=f"Your hand: {player.current_hand.cards} (Score: {player.current_hand.hand_total()}), dealer shows {dealer_upcard}. {choice_indicator} ",
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

        if player.can_split():
            pair_str = f"{dealer_key(player.current_hand.cards[0])}{dealer_key(player.current_hand.cards[1])}" # I guess could just do * 2.
            split_char = pair_splitting[pair_str][dk]
            decision_split = CHAR_TO_WORD[split_char]

            print(f"DEBUG: Decision to split: {decision_split} with {player.current_hand.cards} and DK: {dk}")
            print(f"DEBUG: Bankroll: ${player.bankroll}, Cur bet: {player.current_hand.bet}")
            if len(player.hands_collection) > 4:
                raise RuntimeError # Greater than allowed amount of hands bug.
             
            # We allow double after split. Takes away some house advantage (like 0.2% or something).
            if decision_split in ["yes_split", "split_if_double_after_split"]:    
                return "split"
            
        # If soft hand (could refactor to Hand class, when implemented).
        if any(c.rank == "A" for c in player.current_hand.cards) and len(player.current_hand.cards) == 2:
            
            # I don't like the try-except block below, but I think it is needed.
            # What if bankroll low, therefore can't split.
            # This is a potential concern for a player using Basic Strategy
            # Theoretically won't be a concern for card counter player, as long as bankroll is big enough (and correct implementation).
            
            # TODO: Make so can't resplit aces (convention) (i.e., can't split another AA hand if already split an AA hand that round)

            try: 
                other_card = next(c for c in player.current_hand.cards if c.rank != "A")
            except StopIteration:
                return "hit" # Always split on two aces, for now hit.


            # Because the CSV is more readable as just short values (i.e., "H", "D")
            # But this looks bad in CLI.
            soft_total_repr = "A" + str(other_card.value)
            char = soft_totals[soft_total_repr][dk]

        else:
            if hand_total <= 7: return "hit" # Already need to have determined if pair or not (using split/pair logic) for this to be sound.
            row_key = "17+" if hand_total >= 17 else str(hand_total)
            char = hard_totals[row_key][dk]

        decision = CHAR_TO_WORD[char]

        if decision == "double" and not player.can_double():
            return "hit"
        elif decision == "double_if_possible_else_stand":
            return "double" if player.can_double() else "stand"
        return decision


    # TODO: Make this the best it can be.
    def make_bet(self, player):
        tc = player.card_counter.true_count
        table_min = 50 

        if tc > 12:
            units = 12
        else:
            units = max(1, tc)
        
        return min(player.bankroll, table_min * units)

class Players:
    # ROSTER = [
    #     Player("The Pro", BasicStrategy()),
    #     Player("Rational", RationalStrategy()),
    #     Player("Doubler", DoublerStrategy())
    # ]

    ROSTER = []
