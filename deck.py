class Card:
    """Represents a single playing card."""
    
    def __init__(self, rank: str, suit: str):
        self.rank = rank  # e.g., "2", "J", "A"
        self.suit = suit  # e.g., "Hearts", "Spades"

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    @property
    def value(self):
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


def hand_total(hand: list[Card]) -> int:
    """Compute hand value considering Aces as 1 or 11."""
    total = 0
    ace_count = 0

    for card in hand: 
        if card.rank == "A":
            total += 11
            ace_count += 1
        else:
            total += card.value

    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1

    return total

