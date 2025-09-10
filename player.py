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
            if hand_total(player.hand) >= 17:
                return "stand"
            
            # TODO: Make soft/hard bool csv tables, and accompanying logic.
            for card in player.hand:
                if card.rank == "A": # soft
                    return None
                raise NotImplementedError # use soft-total decision table
            else:
                raise NotImplementedError # use hard-total decision table
            
        def make_bet(self, player):
            raise NotImplementedError


class Players:
    ROSTER = [
        Player("Random", RandomStrategy()),
        Player("Rational", RationalStrategy()),
        Player("Doubler", DoublerStrategy())
    ]

    # ROSTER = []





    

