from deck import Card

class CardCounter:
    def __init__(self):
        self.running_count: int
        self.true_count: int
        self.decks_remaining: float

    def reset_counts(self) -> None:
        self.running_count = 0
        self.true_count = 0

    def update_counts(self, card: Card, n: float) -> None:
        self.decks_remaining = n
        self.running_count += card.hilo_value
        self.true_count = int(self.running_count / self.decks_remaining)

        print(f"DEBUG: rc: {self.running_count}, tc: {self.true_count}")