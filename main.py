from manager import Manager
from messages import Messages
from session import Session
from player import Player, Players, HumanStrategy, BasicStrategy

MAX_ROUNDS = 10000000

if __name__ == "__main__":

    print(Messages.ASCII_TITLE)

    print(f"\n\033[3m{Messages.WELCOME_MESSAGE}\033[23m") # ANSI Escape Code for italics 

    # print(f"\n{Messages.WELCOME_MESSAGE}")
    start_choice = Manager.handle_input(
        Messages.START_CHOICE_MESSAGE, 
        choices=["play", "game", "sim"], 
        input_type=str, 
        invalid_message="That wasn't one of the choices.")

    if start_choice in ["play", "game"]:
        name = Manager.handle_input(
            Messages.NAME_REQUEST, 
            input_type=str,      
            is_name=True)
        
        Players.ROSTER.append(Player(name, HumanStrategy())) # Human always at last "seat" of "table"
        session = Session(Players.ROSTER)
        session.play_session()

    else: # sim
        Players.ROSTER.append(Player("The Pro", BasicStrategy())) # Human always at last "seat" of "table"
        n_rounds = Manager.handle_input(
            Messages.N_ROUNDS, 
            input_type=int, 
            validator=lambda x: 1<=x<=MAX_ROUNDS,
            invalid_message=f"Please choose a number between 1 and {MAX_ROUNDS}")
        session = Session(Players.ROSTER, n_rounds)
        session.play_session()



    
