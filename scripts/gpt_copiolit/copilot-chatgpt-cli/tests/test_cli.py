import unittest
from unittest.mock import MagicMock, patch

from src.copilot_chat import main


class TestCLI(unittest.TestCase):
    @patch("builtins.input", side_effect=["Hello, ChatGPT!", "exit"])
    @patch("src.copilot_chat.ChatGPTClient")
    def test_chatgpt_interaction(self, mock_client_cls: MagicMock, mock_input: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.get_response.return_value = "Hello! How can I assist you today?"

        with patch("sys.stdout", new_callable=MagicMock) as mock_stdout:
            main()

        mock_client.get_response.assert_called_once_with("Hello, ChatGPT!")
        mock_stdout.write.assert_any_call("Hello! How can I assist you today?")
        mock_input.assert_called()

    @patch("builtins.input", side_effect=["invalid input", "exit"])
    @patch("src.copilot_chat.ChatGPTClient")
    def test_invalid_input(self, mock_client_cls: MagicMock, mock_input: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.get_response.return_value = "I'm sorry, I didn't understand that."

        with patch("sys.stdout", new_callable=MagicMock) as mock_stdout:
            main()

        mock_client.get_response.assert_called_once_with("invalid input")
        mock_stdout.write.assert_any_call("I'm sorry, I didn't understand that.")
        mock_input.assert_called()


if __name__ == "__main__":
    unittest.main()
