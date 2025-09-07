from player import Player, HumanStrategy
from shoe import Shoe
from deck import Card, hand_total


class Round:
    """Defines a single Blackjack round."""
    
    def __init__(self, players: list[Player], shoe: Shoe, interactive: bool):
        self.players = players
        self.shoe = shoe
        self.interactive = interactive
        self.dealer_hand: list[Card] = []

    def play_round(self):
        
        # --- Removal Check ---
        for player in self.players[:]:  # iterate over a shallow copy
            if player.bankroll <= 0:
                print(f"{player.name} was removed from the game for having no bankroll left!")
                if isinstance(player.strategy, HumanStrategy): # Not (yet?) designed for multiple humans
                    print(f"That means you, {player.name}... get your strategy down, then show everyone what you're made of!")
                    return "stop_session"
                self.players.remove(player)

        # --- Bets ---
        for player in self.players:
            player.current_bet = player.make_bet()
            if self.interactive:
                print(f"{player.name} bets {player.current_bet}")

        # --- Initial deal ---
        for player in self.players:
            player.hand = [self.shoe.deal_card(), self.shoe.deal_card()]
        self.dealer_hand = [self.shoe.deal_card(), self.shoe.deal_card()]

        dealer_upcard = self.dealer_hand[0]
        if self.interactive:
            print(f"Dealer shows {dealer_upcard}")

        # --- Check for natural Blackjack's (auto-win) ---
        dealer_total = hand_total(self.dealer_hand)
        for player in self.players:
            player_total = hand_total(player.hand)
            if player_total == 21:
                if dealer_total == 21:
                    # Push
                    if self.interactive:
                        print(f"{player.name} and dealer both have Blackjack! Push.")
                else:
                    # Player wins 1.5× bet
                    if self.interactive:
                        print(f"{player.name} has Blackjack! Wins 1.5x bet.")
                    player.bankroll += int(1.5 * player.current_bet)
                player.current_bet = 0 # Round over for this player

        # --- Player turns ---
        for player in self.players:
            while True:
                if self.interactive:
                    print(f"{player.name}'s hand: {player.hand} (Total: {hand_total(player.hand)})")
                decision = player.make_decision(dealer_upcard)
                if decision == 'hit':
                    player.hand.append(self.shoe.deal_card())
                    if hand_total(player.hand) > 21:
                        if self.interactive:
                            print(f"{player.name} busts with {player.hand} (Total: {hand_total(player.hand)})")
                        player.bankroll -= player.current_bet
                        player.current_bet = 0
                        break
                elif decision == 'stand':
                    break

        # --- Dealer turn ---
        if self.interactive:
            print(f"Dealer's full hand: {self.dealer_hand} (Total: {hand_total(self.dealer_hand)})")
        dealer_total = hand_total(self.dealer_hand)
        
        # Casino convention: dealers hit to 16
        while dealer_total < 17:
            self.dealer_hand.append(self.shoe.deal_card())
            dealer_total = hand_total(self.dealer_hand)
            if self.interactive:
                print(f"Dealer hits: {self.dealer_hand} (Total: {dealer_total})")
        
        # --- Resolve bets ---
        for player in self.players:
            if player.current_bet == 0:
                continue  # already busted
            player_total = hand_total(player.hand)
            if dealer_total > 21 or player_total > dealer_total:
                player.bankroll += player.current_bet  # player wins
                result = "wins"
            elif player_total == dealer_total:
                result = "push"
            else:
                player.bankroll -= player.current_bet  # player loses
                result = "loses"
            if self.interactive:
                print(f"{player.name} {result} (Hand: {player.hand}, Dealer: {self.dealer_hand})")
            player.current_bet = 0

        # --- Recycle shoe if using CSM ---
        self.shoe.csm_recycle()
