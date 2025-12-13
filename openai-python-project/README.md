# OpenAI Python Project

This project demonstrates how to interact with the OpenAI API using Python. It includes a simple script that initializes the OpenAI client and sends prompts to the GPT-5 model.

## Project Structure

```
openai-python-project
├── src
│   ├── eq12_agent_runner.py  # Main script to run the OpenAI API
│   └── config.json           # Configuration file for storing the OpenAI API key
├── .vscode
│   └── launch.json           # VS Code launch configuration
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   Clone this repository to your local machine using:
   ```
   git clone <repository-url>
   ```

2. **Install Dependencies**
   Navigate to the project directory and install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. **Configure Credentials**
   Add your API keys to `keys/credentials.json` (for example set `openai.api_key`). You can edit the JSON directly or run any script once and provide values when prompted. The configuration files under `src/` now only document which key path is used.
4. **Run the Script**
   You can run the script directly from the terminal:
   ```
   python src/eq12_agent_runner.py
   ```
   Alternatively, you can use the VS Code launch configuration. Open the command palette (Ctrl+Shift+P) and select "Run Without Debugging" or simply press F5.

## Usage

The `eq12_agent_runner.py` script contains an example prompt that demonstrates how to use the GPT-5 model. Modify the prompt in the script to test different queries.

## Notes

- Ensure that your OpenAI API key is kept secure and not shared publicly.
- The `config.json` file should only be updated when the API key is rotated.