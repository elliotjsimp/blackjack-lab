class Card:
    """Represents a single playing card."""
    def __init__(self, rank: str, suit: str):
        self.rank = rank  # e.g., "2", "J", "A"
        self.suit = suit  # e.g., "Hearts", "Spades"

    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    def __repr__(self):
        return f"{self.rank}"
    
    @property
    def value(self) -> int:
        """Returns the Blackjack value of a card."""
        if self.rank in ["J", "Q", "K"]:
            return 10
        elif self.rank == "A":
            return 11  # switches to 1 in hand_total() if necessary.
        else:
            return int(self.rank)
    
    @property
    def hilo_value(self) -> int:
        "Returns the Hi-Lo value of a card."
        if self.value in [2,3,4,5,6]: return 1
        elif self.value in [10, 11]: return -1
        return 0

class Deck:
    """Represents a deck of cards."""

    suits = ["♥", "♦", "♣", "♠"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self):
        # Create a full deck of Card objects
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]




