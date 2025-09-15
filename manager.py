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
        message: str,                   # Message to show for input
        *,                              # Force pass by keyword for following:
        choices: list[str] = None,      # Optional: For string input choices
        input_type: type,               # The valid input type for this call
        validator=None,                 # Optional: Only used for valid range of int lambda function currently.
        invalid_message: str = None,    # Optional: Message to be printed if validator false, or not in choices.
        is_name: bool = False           # Somewhat Band-Aid solution to get actual casing of name input, but works.
    ):
        """
        Generalized input handler.

        Args:
        - message: Prompt to show
        - choices: Optional list of valid string options
        - input_type: Type to convert input to (int, str, float)
        - validator: Optional function(input) -> bool for custom validation (only used to get correct range for ints)
        - invalid_message: Message to show if validator false
        - is_name: Flag to determine if we should return raw string input (instead of lowered).
        """
        while True:
            raw = input(f"\n{message}").replace(" ", "")
            lower_raw = raw.lower()

            if lower_raw in Messages.QUIT_CHOICES:
                Manager.quit_game()

            # If expecting string input, reject numeric-looking entries up front
            if input_type is str:
                try:
                    float(raw) # Succeeds if numeric-like
                    print("Invalid input type.")
                    continue
                except ValueError:
                    pass # Therefore not numeric so all good

            try:
                value = input_type(raw) # Now attempt to cast into the expected type
            except ValueError:
                print("Invalid input type.")
                continue
            
            # Check if in choices
            if choices and (lower_raw not in [c.lower() for c in choices]):
                print(invalid_message) # W
                continue
            
            # Currently only used for range check to get n_rounds in main.py, when start_choice is sim
            if validator and not validator(value): # Using lambda function
                print(invalid_message)
                continue

            # Show spinner (fake loading) before input is returned
            Manager.show_spinner()

            if input_type is str:
                # So we don't return lower for HumanStrategy Player name (i.e., the user, LOL)
                return raw if is_name else lower_raw 
            return value