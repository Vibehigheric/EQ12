def validate_input(user_input: str) -> bool:
    """Validate user input to ensure it meets the required criteria."""
    return bool(user_input.strip())


def format_response(response: str) -> str:
    """Format the response from the ChatGPT API for display."""
    return response.strip()


def log_error(error_message: str) -> None:
    """Log an error message to the console or a log file."""
    print(f"Error: {error_message}")


def parse_command(command: str) -> str:
    """Parse the user command and return a standardized format."""
    return command.lower().strip()
