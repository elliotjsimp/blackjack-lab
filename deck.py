class Card:
    """Represents a single playing card."""
    
    def __init__(self, rank: str, suit: str):
        self.rank = rank  # e.g., "2", "J", "A"
        self.suit = suit  # e.g., "Hearts", "Spades"

    # Used in round.py
    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    
    def __repr__(self):
        return f"{self.rank}"
    
    # NOTE:
    # __str__() would maybe be fully worded then, i.e., "Four of Diamonds".
    # IDK what the value of this would be though, unless for some type of GUI.

    @property
    def value(self) -> int:
        """Returns the Blackjack value of the card."""
        if self.rank in ["J", "Q", "K"]:
            return 10
        elif self.rank == "A":
            return 11  # or 1 depending on hand logic
        else:
            return int(self.rank)

        
class Deck:
    """Represents a deck of cards."""

    suits = ["♥", "♦", "♣", "♠"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self):
        # Create a full deck of Card objects
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]




