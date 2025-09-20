import sys
import itertools
import time
from messages import Messages


class Manager:
    """Manages user input, quitting, and the "spinner" output. All methods are static."""

    @staticmethod
    def quit_game():
        print("Have a great day! The program has quit.\n")
        sys.exit()


    @staticmethod
    def show_spinner(duration: float = 0.5) -> None:
        """Shows a spinner to imitate loading (to make outputs less jarring for users)."""
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        start_time = time.time()
        while time.time() - start_time < duration:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(0.1)
        # Clean last spinner character
        sys.stdout.write(' ')
        sys.stdout.write('\b')


    @staticmethod
    def handle_input(
        message: str,
        *,                         # Force pass by keyword for following
        choices: list[str] = None, # For string input choices
        input_type: type,    
        validator=None,            # Only used for valid range of int lambda function
        invalid_message: str = None,
        is_name: bool = False      # Somewhat band-aid solution to get actual casing of name input 
    ):
        """
        Generalized input handler.

        - message: Prompt to show
        - choices: Optional list of valid string options
        - input_type: Type to convert input to (int, str, float)
        - validator: Optional function(input) -> bool for custom validation (only used to get correct range for ints)
        - invalid_message: Message to show if validator false
        """
        while True:
            raw = input(f"\n{message}").replace(" ", "")
            lower_raw = raw.lower()

            if lower_raw in Messages.QUIT_CHOICES:
                Manager.quit_game()

            # If expecting string input, reject numeric-looking entries up front
            if input_type is str:
                try:
                    float(raw)  # Succeeds if numeric-like
                    print("Invalid input type.")
                    continue
                except ValueError:
                    pass  # Therefore not numeric so all good

            # Now attempt to cast into the expected type
            try:
                value = input_type(raw)
            except ValueError:
                print("Invalid input type.")
                continue

            if choices and (lower_raw not in [c.lower() for c in choices]):
                print("Choice not in allowed options.")
                continue

            if validator and not validator(value):
                print(invalid_message)
                continue

            if input_type is str:
                # So we don't return lower for HumanStrategy Player name (i.e. the user, LOL)
                # This probably isn't the best solution in the world but all good
                Manager.show_spinner()
                return raw if is_name else lower_raw 
            else:
                Manager.show_spinner()
                return value