from abc import ABC, abstractmethod
import random
from manager import Manager
from deck import Card, hand_total

class Strategy(ABC):
    @abstractmethod
    def make_decision(self, hand: list[Card], dealer_upcard, **kwargs) -> str:
        pass

    @abstractmethod
    def make_bet(self, bankroll: int, **kwargs) -> int:
        pass


class RandomStrategy(Strategy):
    """Random, but rational. Stands at 21."""
    def make_decision(self, hand: list[Card], dealer_upcard, **kwargs) -> str:
        # Not worth simulating complete irrationality. Need to stand at 21.
        if hand_total(hand) == 21:
            return 'stand'
        return random.choice(['hit', 'stand'])

    def make_bet(self, bankroll: int, **kwargs) -> int:
        # Random bet between 10% and 25% of bankroll
        return max(1, int(bankroll * random.uniform(0.1, 0.25))) // 1


class RationalNaiveStrategy(Strategy):
    """Follows dealer logic, stands at 17 or more."""
    def make_decision(self, hand: list[Card], dealer_upcard, **kwargs) -> str:
        if hand_total(hand) < 17:
            return 'hit'
        return 'stand'
    def make_bet(self, bankroll: int, **kwargs) -> int:
        return bankroll * 0.15 // 1 # Bets 15% of bankroll (my arbitrary choice)
    


class HumanStrategy(Strategy):
    """HumanStrategy... the fate of the game is left in your mortal hands!"""
    def make_decision(self, hand: list[Card], dealer_upcard, **kwargs) -> str:
        return Manager.handle_input(
            message=f"Your hand: {hand} (Score: {hand_total(hand)}), dealer shows {dealer_upcard}. Hit or stand? ",
            choices=["hit", "stand"]
        )

    def make_bet(self, bankroll: int, **kwargs) -> int:
        return Manager.handle_input(
            message=f"Your bankroll: {bankroll}. Enter your bet amount: ",
            input_type=int,
            validator=lambda x: 0 < x <= bankroll,
            invalid_message="That wasn't a valid bet."
        )


class Player:
    def __init__(self, name: str, strategy: Strategy, bankroll: int = 1000):
        self.name = name
        self.strategy = strategy
        self.bankroll = bankroll
        self.current_bet: int = 0
        self.hand: list[Card] = []

    def make_decision(self, dealer_upcard, **kwargs) -> str:
        return self.strategy.make_decision(self.hand, dealer_upcard, **kwargs)

    def make_bet(self) -> int:
        return self.strategy.make_bet(self.bankroll)

    

class Players:
    ROSTER = [
        Player("Random1", RandomStrategy()),
        Player("Random2", RandomStrategy()),
        Player("Rational", RationalNaiveStrategy())
    ]





    

