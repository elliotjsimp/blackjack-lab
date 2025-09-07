import sys
from messages import Messages

class Manager:
    """Manages user input and quitting."""

    @staticmethod
    def handle_input(
        message: str,
        *,                         # Force pass by keyword for following
        choices: list[str] = None, # For string input choices
        input_type: type = str,    
        validator=None,            # Only used for valid range of int lambda function
        invalid_message: str = None
    ):
        """
        Generalized input handler.

        - message: Prompt to show
        - choices: Optional list of valid string options
        - input_type: Type to convert input to (int, str, float)
        - validator: Optional function(input) -> bool for custom validation
        - invalid_message: Message to show if validator false
        """
        while True:
            raw = input(f"\n{message}").strip()
            lower_raw = raw.lower().replace(" ", "")

            if lower_raw in Messages.QUIT_CHOICES:
                Manager.quit_game()

            try:
                value = input_type(raw)
            except ValueError:
                print("Invalid input type.")
                continue

            if choices and str(value).lower() not in [c.lower() for c in choices]:
                print("Choice not in allowed options.")
                continue

            if validator and not validator(value):
                print(invalid_message)
                continue

            return value
    
    @staticmethod
    def print_banner(message: str):
        print(f"\n{message}\n")


    @staticmethod
    def quit_game():
        print("Have a great day! The program has quit.")
        sys.exit()
