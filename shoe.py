from deck import Deck, Card
import random

class Shoe:
    def __init__(self, deck_count: int=6, penetration: float=0.75, use_csm: bool=False):
        self.deck_count = deck_count
        self.penetration = penetration  # Most casinos reshuffle the shoe when 75% of the cards have been used (4/6 decks).
        self.use_csm = use_csm
        self.cards = []
        self.discards = []
        self.build_shoe()

    @property
    def cut_card_position(self):
        return int(52 * self.deck_count * (1 - self.penetration))

    def build_shoe(self):
        # print("Debug: Building Shoe")
        self.cards.clear()
        self.discards.clear()
        for _ in range(self.deck_count):
            self.cards.extend(Deck().cards)
        self.shuffle()
        
    def shuffle(self):
        """Shuffle the shoe."""
        # print("Debug: Shuffling the shoe.")
        random.shuffle(self.cards)

    def deal_card(self) -> Card:
        """Deal a card from the shoe."""
        # Automatic reshuffle if necessary based on penetration into shoe (not csm)
        if not self.use_csm and len(self.cards) < self.cut_card_position:
            self.build_shoe()

        # Debug Messages to ensure that shoe behaves as expected
        # Shoe must rebuild (therefore reshuffle also) when 75% penetrated (4/6 decks in discards "pile")
        # penetration_percent = 100 * (len(self.discards) / (self.deck_count * 52))
        # print(f"Debug: Penetration is {penetration_percent:.2f}%")

        card = self.cards.pop()
        self.discards.append(card) # Technichally don't need if not use_csm, but might as well for analysis...
        return card
    
    def csm_recycle(self):
        """Use the CSM to recycle discards back into the shoe."""
        if self.use_csm and self.discards:
            
            # Faking the "Continuous" in "Continuous Shuffle Machine:
            # Insert shuffled discards into shoe at random insertion point
            # Using empty slice so no cards are removed from shoe

            # print("DEBUG: Using CSM.")
            random.shuffle(self.discards)
            insertion_point = random.randint(0, len(self.cards))
            self.cards[insertion_point:insertion_point] = self.discards
            self.discards.clear()

