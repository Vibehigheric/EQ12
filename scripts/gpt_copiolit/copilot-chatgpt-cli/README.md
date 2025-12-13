# copilot-chatgpt-cli

## Overview
The Copilot ChatGPT CLI is a command-line interface that allows users to interact with the ChatGPT API. This project facilitates seamless communication between users and the ChatGPT model, enabling various functionalities through simple terminal commands.

## Features
- User-friendly command-line interface for interacting with ChatGPT.
- Ability to send messages and receive responses from the ChatGPT API.
- Configuration management for API keys and settings.
- Utility functions for input validation and response formatting.
- Comprehensive testing suite to ensure reliability and correctness.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/copilot-chatgpt-cli.git
   cd copilot-chatgpt-cli
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy the `.env.example` to `.env` and fill in your API keys and other configuration settings.

## Usage
To start the CLI, run the following command:
```
python src/copilot_chat.py
```

You can then enter your queries, and the CLI will communicate with the ChatGPT API to provide responses.

## Testing
To run the tests, use the following command:
```
pytest
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.