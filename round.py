from player import Player, HumanStrategy 
from manager import Manager
from shoe import Shoe
from deck import Card
from hand import Hand
from collections import deque


BANNER_LEN = 45 # amount of "=" that prints is multiplied by this constant (for per-round print methods)


class Round:
    """Defines a single Blackjack round."""

    def __init__(self, players: list[Player], shoe: Shoe, round_number: int, interactive: bool):
        self.players = players
        self.shoe = shoe
        self.round_number = round_number
        self.interactive = interactive
        self.dealer_hand: Hand
        self.decisions = {player: [] for player in self.players}
        # TODO: Refactor to per-hand dict, per player (in player object, I think... or maybe separate object to track data?)
        # Whatever is best for matplotlib usage, or simply, whatever is best for large amount of rounds.


    def dealer_upcard(self) -> Card:
        return self.dealer_hand.cards[0]


    def removal_check(self) -> str | None:
        """Check for possible removal of a player. Players are removed if zero bankroll."""
        for player in self.players[:]: # Create shallow copy so we can iterate and remove safely at same time
            if player.bankroll <= 0:
                print(f"\n{player.name} was removed from the game for having no bankroll left!") # Could use interactive flag here in the future.
                if isinstance(player.strategy, HumanStrategy): # Not designed for multiple humans, therefore quit.
                    print(f"That means you, {player.name}... get your strategy down, then show everyone at the tables what you're made of!\n")
                    return "stop_session"
                self.players.remove(player)
        return None

            
    def deal_initial_hands(self) -> None:
        """Deal initial hands for all players."""
        for player in self.players:
            
            player.per_hand_result = {}
            player.final_hands = []
            player.hands_collection = deque()

            player.current_hand.add_card(self.shoe.deal_card())
            player.current_hand.add_card(self.shoe.deal_card())
            player.hands_collection.append(player.current_hand)

        self.dealer_hand = Hand()
        self.dealer_hand.add_card(self.shoe.deal_card())
        self.dealer_hand.add_card(self.shoe.deal_card())


    def initial_blackjack_check(self) -> None:
        """Check for initial Blackjack's (sometimes called a Natural Blackjack) (auto-win the round)."""
        dealer_total = self.dealer_hand.hand_total()
        for player in self.players:
            player_total = player.current_hand.hand_total()
            if player_total == 21:
                if dealer_total == 21:
                    # Push (tie with dealer) Blackjack, very rare!
                    player.bankroll += player.current_hand.bet # add back
                    player.per_hand_result[player.current_hand] = ["push blackjack"]

                else:
                    # Blackjack, Player wins 3:2 their bet
                    player.per_hand_result[player.current_hand] = ["blackjack"]
                    player.bankroll += int(2.5 * player.current_hand.bet)
                player.hands_collection.clear() # Round over for player.

    
    """""
    # TODO: Fully depreciate usage of this method, in favour of player_turns_with_split
    def player_turns(self) -> None:
        All player turns. The "meat" of the game, in my opinion.
        for player in self.players:
            # This works because human is always at last index of players/last "seat", therefore table is ready to print.
            # This is generally prefered by IRL card-counters (if they play at a table with other people, that is).
            if isinstance(player.strategy, HumanStrategy): self.print_table_moves()

            # TODO: Make bust method for DRY.
            while True:
                if player.current_bet > 0:
                    decision = player.make_decision(self.dealer_upcard()) # Dealer upcard passed as argument
                    self.decisions[player].append(decision)

                    if decision in ["hit", "h"]:
                        player.hands_collection[0].add_card(self.shoe.deal_card())

                        if player.hands_collection[0].hand_total() > 21:
                            self.decisions[player].append("bust")

                            player.bankroll -= player.current_bet
                            player.current_bet = 0
                            break
                    elif decision in ["stand", "s"]:
                        break
                    elif decision in ["double", "d"]: # doubling in Blackjack is effectively double bet, then hit.
                        # NOTE: Valid doubling is handled by each Strategy instance now. Maybe not the best solution...
                        player.current_bet *= 2

                        if isinstance(player.strategy, HumanStrategy):
                            print(f"You doubled your bet to ${player.current_bet}...")

                        player.hands_collection[0].add_card(self.shoe.deal_card())

                        if player.hands_collection[0].hand_total() > 21:
                            self.decisions[player].append("bust")

                            player.bankroll -= player.current_bet
                            player.current_bet = 0
                            break

                else:
                    break   # For players in for loop who have hit Blackjack (push or not (tie with dealer or not))),
                            # The "dealer" (else break code) forces them to be rational in these cases, and not play.
                            # We could apend "stand" here, but would be messy in tables/data.
    """

    def player_turns_with_split(self) -> None:
        """A WIP method to replace the player_turns method. Supports splitting hands."""

        for player in self.players:
            
            # Human player is always at last seat of "table", therefore they can see everything thus far.
            if player.is_human(): self.print_table_moves() 

            while player.hands_collection:
                player.current_hand = player.hands_collection.popleft()
                player.per_hand_result[player.current_hand] = []

                while True:

                    if player.current_hand.hand_total() == 21:
                        decision = "stand"
                    else:
                        decision = player.make_decision(self.dealer_upcard()) # And need to ensure make_decision correctly uses parameter current_hand.

                    match decision:
                        case "hit" | "h":
                            player.current_hand.add_card(self.shoe.deal_card()) # Could simplify this syntax length-wise for all calls probably.
                            player.per_hand_result[player.current_hand].append("hit") # Is this okay?

                            if player.handle_bust():
                                player.record_cur_hand()
                                break

                            continue

                        case "stand" | "s":
                            # Don't really need to add "stand" to history, at least for display purposes...
                            player.per_hand_result[player.current_hand].append("stand")

                            player.record_cur_hand()
                            break
                        
                        case "double" | "d":
                            if not player.can_double():
                               
                                # NOTE: Pretty sure fixed bug so that this won't happen anymore.
                                # Was because can_double method wasn't considering the fact
                                # That we properly handle subtracting bet from bankroll at start of round.
                                print("Uh oh, this will cause an infinite loop!")
                                print(f"{player.name} wants to double... can they?: {str(player.can_double())}")
                                print(f"Current bet: {player.current_hand.bet}, Bankroll: {player.bankroll}")
                                raise RuntimeError

                            player.bankroll -= player.current_hand.bet
                            if player.bankroll < 0: raise RuntimeError
                            player.current_hand.bet *= 2

                            if player.bankroll == 0: print("You're all in!")
                            
                            player.current_hand.add_card(self.shoe.deal_card())
                            player.per_hand_result[player.current_hand].append("double")

                            if player.handle_bust():
                                player.record_cur_hand()
                                break

                            continue

                        case "split":
                            can_split = player.can_split()
                            is_pair = player.current_hand.is_pair()
                            
                            if can_split and is_pair:

                                new_hand1 = Hand()
                                new_hand1.bet = player.current_hand.bet
                                
                                new_hand2 = Hand()
                                new_hand2.bet = player.current_hand.bet
                                player.bankroll -= player.current_hand.bet
                                if player.bankroll < 0: raise RuntimeError

                                new_hand1.add_card(player.current_hand.cards[0])
                                new_hand2.add_card(player.current_hand.cards[1])

                                new_hand1.add_card(self.shoe.deal_card())
                                new_hand2.add_card(self.shoe.deal_card())

                                # Put new hands to the front of the queue (ensures correct playing order)
                                player.hands_collection.appendleft(new_hand2)
                                player.hands_collection.appendleft(new_hand1)

                                player.per_hand_result[player.current_hand].append("split")
                                player.record_cur_hand() # Because we used popleft to access current hand.

                                all_hands = ", ".join(str(h.cards) for h in player.hands_collection)
                                # completed_hands = ", ".join(str(h.cards) for h in player.final_hands)

                                print(f"Pending hands: {all_hands}")
                                # print(f"Completed hands: {completed_hands}") # Includes hands that weren't yet split. Doesn't make sense to user.
                                break

                            else:
                                if player.is_human():
                                    # Wait, we should be handling this with handle_input...
                                    if not can_split and is_pair:
                                        msg = "You aren't allowed to split!"
                                    else:
                                        # Even if player cannot split (bankroll or too many hands), focus on the most pressing issue: their cards aren't a pair.
                                        # NOTE: Hopefully never see this msg if we handle logic correctly, specifically for human choices list for input.
                                        msg = "Your cards aren't a pair!" 

                                    print(f"That wasn't a valid move... {msg}")

                                continue
                        case _:
                            print(f"DEBUG: A strategy incorrectly returned {decision}")
                            raise RuntimeError # Some Strategy has returned an invalid decision...


    def resolve_bets(self, dealer_total: int) -> None: # --- Resolve bets ---
        """NOTE: Technichally, we are more like finalizing bankroll adjustments.
        Semantic difference, but it would be better perhaps if we directly modified
        Player bankroll at start of round (when bet occurs).
        Now, we are displaying "new" bankroll in print_bets method, but not actually changing until after round play.
        Should probably just parody real-world.
        I guess I just didn't want to subtract, then add back... but doesn't need to be operation-optimized like this."""

        for player in self.players:
            for hand in player.final_hands:

                hand_total = hand.hand_total()
                hand_result = player.per_hand_result[hand][-1] # Last result for hand. # THIS IS BUGGY LINE.

              
                if hand_result in ["stand", "hit"]: # would ever be hit? I don't think so...
                    # Bust logic already handled by this point.
                    if (hand_total > dealer_total) or (dealer_total > 21 and hand_total < 21):
                        player.bankroll += (hand.bet * 2)
                        player.per_hand_result[hand].append("wins")
                    elif hand_total == dealer_total:
                        player.bankroll += hand.bet
                        player.per_hand_result[hand].append("push")
                    else:
                        player.per_hand_result[hand].append("loses")

                hand_result = player.per_hand_result[hand][-1] # Last result for hand.

                # TODO: Implement table print method instead of this placeholder.
                if hand_result == "split":
                    print(f"{player.name} {hand_result} a ${hand.bet} hand...")
                else:
                    print(f"{player.name} {hand_result} ${hand.bet}")

                    # DEBUG
                    print(f"Player: {hand.cards}, ({hand_total})")
                    print(f"Dealer: {self.dealer_hand.cards}, ({dealer_total})")



    def play_round(self):
        """Handles core round logic. I've tried to provide an ample amount of comments, mainly
        for people who may not know how Blackjack works."""

        remove = self.removal_check()
        if remove: return remove

        print(f"\nRound Number {self.round_number}")


        # --- Take Bets ---
        for player in self.players:
            player.current_hand = Hand()
            player.current_hand.bet = player.make_bet()
            player.bankroll -= player.current_hand.bet # New
            if player.bankroll < 0: raise RuntimeError
        
        # Print the bets table.
        self.print_bets()

        # Deal initial hands to players.
        self.deal_initial_hands()
        
        # Print the initial deal table.
        self.print_initial_deal()

        # Check for player Blackjack's. Player wins 3:2 their bet.
        self.initial_blackjack_check()

        # Compute player turns.
        self.player_turns_with_split()

        # Dealer's turn
        dealer_total = self.dealer_hand.hand_total() # TODO: Why calling twice? Messy. Fix. I guess need to though.
        while dealer_total < 17: # Casino Convention: most dealers stand at 17 (soft or hard).

            self.dealer_hand.add_card(self.shoe.deal_card())
            dealer_total = self.dealer_hand.hand_total()
            # if self.interactive: print(f"Dealer hits: {self.dealer_hand} (Total: {dealer_total})")

        if self.interactive: print(f"\nDealer's full hand: {self.dealer_hand.cards} (Total: {self.dealer_hand.hand_total()})\n")

        # Resolve all player bets (please see docstring for important detail).
        self.resolve_bets(dealer_total)

        # Recycle shoe if using CSM (usually not, as it is not prefered).
        self.shoe.csm_recycle()


    # Please forgive my non-DRY (wet, if you will) implementations of the following print methods:
    def print_bets(self) -> None:
        """"""
        # if not self.interactive: return None
        # Manager.show_spinner()
        print("\n","="*BANNER_LEN, sep="")
        print(f"Round {self.round_number} Bets")
        print("="*BANNER_LEN)
        print("\nPlayer     | Bet          | New Bankroll") 
        print("-----------+--------------+--------------")
        for player in self.players:
            print(f"{player.name:<10} | {f'${player.current_hand.bet}':>12} | ${player.bankroll}")


    def print_initial_deal(self) -> None:
        """Prints the initial deal table, with the dealer upcard."""
        if not self.interactive: return None
        Manager.show_spinner(0.8) # Slightly longer

        print("\n","="*BANNER_LEN, sep="")
        print("Initial Deal")
        print("="*BANNER_LEN)
        print(f"\nDealer Shows {self.dealer_upcard()}") # Dealer upcard
        print("\nPlayer     | Hand              | Total") 
        print("-----------+-------------------+-------")

        for player in self.players:
            # We know only one hand per player on initial deal.
            hand_str = ", ".join(str(card) for card in player.current_hand.cards)
            print(f"{player.name:<10} | {hand_str:<17} | {player.current_hand.hand_total()}")

    
    # TODO: Normalize naming convention project-wide (move vs decision... which?)
    def print_table_moves(self) -> None:
        """Prints the turns of all other players in order. To be used before HumanStrategy needs to make decision.""" # TODO: Make docstring more clear LOL
        if not self.interactive: return None
        Manager.show_spinner(0.8) # Slightly longer

        if len(self.players) <= 1: return None # if only HumanStrategy in self.players (ROSTER is hardcoded right now though).
        print("\n","="*BANNER_LEN, sep="")
        print("Table Moves") # TODO: Need better, more Blackjack native, titles where applicable, like here.
        print("="*BANNER_LEN)
        # TODO: Make it so the table width expands if needed to accomodate a player's big hand. Therefore won't need to be so ugly-wide by default.
        print("\nPlayer     | Hand                      | Move(s)")
        print("-----------+---------------------------+---------")

        for player in self.players:
                for hand in player.final_hands:

                    hand_str = ", ".join(str(card) for card in hand.cards)

                    # `d` is each str in array of str's as the value of decisions dict, with Player object as key.
                    decisions_str = ", ".join(d.upper() for d in player.per_hand_result[hand])

                    # NOTE: I could not print STAND if that's the last dedecision in decision_str (because redundant)
                    print(f"{player.name:<10} | {hand_str:<19}       | {decisions_str}")


    def print_round_results(self):
        raise NotImplementedError
