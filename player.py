from __future__ import annotations 
"""The above makes it so we can do Strategy class, 
then player class (or vice versa). We don't need 
to worry about not yet defined, or circular imports.
Basically asks Python to treat all type definitions 
in functions as strings until everything is defined)."""

import random
from manager import Manager
from deck import Card, hand_total
from abc import ABC, abstractmethod
import csv

# Used to convert from CSV move to game move (so printed tables don't have letters, 
# even though they are valid for humans to type as moves for convenience).
SHORT_TO_LONG = {
    "H":"hit",
    "S":"stand",
    "D":"double",
    "Ds":"double",   # allowed to double is true, therefore double
    "Y": "split",    # UNIMPLEMENTED
    "N": "no_split"  # UNIMPLEMENTED
}


hard_totals_path="hard_totals.csv"
soft_totals_path="soft_totals.csv"
hard_totals = {}
soft_totals = {}

# Load hard totals
with open(hard_totals_path) as htp:
    reader = csv.DictReader(htp)
    for row in reader:
        key = row["Player Total"].strip()  # strip spaces
        hard_totals[key] = {dealer.strip(): row[dealer].strip() for dealer in row if dealer != "Player Total"}

# Load soft totals
with open(soft_totals_path) as stp:
    reader = csv.DictReader(stp)
    for row in reader:
        key = row["Player Total"].strip()
        soft_totals[key] = {dealer.strip(): row[dealer].strip() for dealer in row if dealer != "Player Total"}

def dealer_key(card: Card):
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
        self.hand: list[Card] = []

    def make_decision(self, dealer_upcard: Card=None) -> str:
        return self.strategy.make_decision(self, dealer_upcard)
    
    def make_bet(self) -> int:
        return self.strategy.make_bet(self)


class Strategy(ABC):
    @abstractmethod
    def make_decision(self, player: Player, dealer_upcard: Card) -> str:
        pass

    @abstractmethod
    def make_bet(self, player: Player) -> str:
        pass


# --- Strategy Definitions ---

class RandomStrategy(Strategy):
    """Random choice (but stands at 21)."""
    def make_decision(self, player, dealer_upcard) -> str:
        return "stand" if hand_total(player.hand) == 21 else random.choice(["hit", "stand"])

    def make_bet(self, player) -> int:
        # Random bet between 10% and 25% of bankroll
        return max(1, int(player.bankroll * random.uniform(0.1, 0.25) // 1))


class RationalStrategy(Strategy):
    """Follows dealer logic, stands at 17 or more."""
    def make_decision(self, player, dealer_upcard) -> str:
        if hand_total(player.hand) < 17:
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
    """Double instead of hit, every time."""
    def make_decision(self, player, dealer_upcard) -> str:
        if hand_total(player.hand) < 17:
            return "double" if player.bankroll >= player.current_bet * 2 else "hit" # NOTE: QUICK FIX. SHOULD HANDLE IN ROUND.
        return "stand"
    def make_bet(self, player) -> int:
        return max(1, int(player.bankroll * 0.20 // 1)) # Bets 20% of bankroll


class HumanStrategy(Strategy):
    """HumanStrategy... the fate of the game is left in your mortal hands! But forced to stand at 21."""
    def make_decision(self, player, dealer_upcard) -> str:
        if hand_total(player.hand) == 21: return "stand" # Force stand by "dealer"
        
        return Manager.handle_input(
            message=f"Your hand: {player.hand} (Score: {hand_total(player.hand)}), dealer shows {dealer_upcard}. Hit, stand or double? ",
            choices=["hit", "h", "stand", "s", "double", "d"],
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
        h_total = hand_total(player.hand)
        if h_total >= 20: return "stand"
        if h_total < 8: return "hit"

        if any(c.rank == "A" for c in player.hand) and len(player.hand) == 2:
            # Find the non-ace card
            try:
                other = next(c for c in player.hand if c.rank != "A")
            except StopIteration:
                return "hit"

            soft_total_repr = "A" + str(other.value)
                
            short = soft_totals[soft_total_repr][dealer_key(dealer_upcard)]
            return SHORT_TO_LONG[short]
        else:
            dk = dealer_key(dealer_upcard)
            row_key = "17+" if h_total >= 17 else str(h_total)
            # print(f"DEBUG: row_key={row_key}, dealer_key={dk}, available keys={list(hard_totals[row_key].keys())}")
            short = hard_totals[row_key][dk] # TODO: make method to convert from letter to work
            return SHORT_TO_LONG[short]
        
    def make_bet(self, player):
        return max(1, int(player.bankroll * 0.002 // 1)) # Bets 10% of bankroll for now


class Players:
    # ROSTER = [
    #     Player("The Pro", BasicStrategy()),
    #     Player("Rational", RationalStrategy()),
    #     Player("Doubler", DoublerStrategy())
    # ]

    # ROSTER = []

    ROSTER = [
        Player("The Pro", BasicStrategy(), bankroll=1000),
    ]



    

