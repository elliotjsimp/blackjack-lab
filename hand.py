from deck import Card

class Hand:
    def __init__(self):
        self.cards: list[Card] = []
        self.bet: int
                               

    def hand_total(self) -> int:
        """Compute hand value considering Aces as 1 or 11."""
        total = 0
        ace_count = 0

        for card in self.cards: 
            if card.rank == "A":
                total += 11
                ace_count += 1
            else:
                total += card.value

        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1

        return total
    

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    
    def is_pair(self) -> bool:
        return len(self.cards) == 2 and self.cards[0].value == self.cards[1].value
    

    def has_busted(self) -> bool:
        """Has this hand gone over 21?"""
        return self.hand_total() > 21
            

