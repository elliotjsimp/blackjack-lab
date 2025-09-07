from manager import Manager
from messages import Messages
from session import Session
from player import Player, Players, HumanStrategy

MAX_ROUNDS = 100000

if __name__ == "__main__":
    Manager.print_banner(Messages.WELCOME_MESSAGE)
    start_choice = Manager.handle_input(Messages.START_CHOICE_MESSAGE, choices=["play", "sim"])

    if start_choice == "play":
        name = Manager.handle_input(Messages.NAME_REQUEST)
        Players.ROSTER.append(Player(name, HumanStrategy()))
        session = Session(Players.ROSTER)
        session.play_session()

    elif start_choice == "sim":

        n_rounds = Manager.handle_input(
            Messages.N_ROUNDS, 
            input_type=int, 
            validator=lambda x: 1<=x<=100000, 
            invalid_message=f"Please choose a number between 1 and {MAX_ROUNDS}")
        
        session = Session(Players.ROSTER, n_rounds)
        session.play_session()
    else:
        print("Something messed up!")


    
