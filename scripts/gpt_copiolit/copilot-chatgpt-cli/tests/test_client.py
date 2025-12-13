import unittest

from src.client import ChatGPTClient


class TestChatGPTClient(unittest.TestCase):
    def setUp(self):
        self.client = ChatGPTClient(api_key="test_api_key")

    def test_send_message(self):
        response = self.client.send_message("Hello, ChatGPT!")
        self.assertIsInstance(response, str)
        self.assertNotEqual(response, "")

    def test_receive_response(self):
        self.client.send_message("Hello, ChatGPT!")
        response = self.client.receive_response()
        self.assertIsInstance(response, str)
        self.assertNotEqual(response, "")

    def test_api_key_initialization(self):
        self.assertEqual(self.client.api_key, "test_api_key")


if __name__ == "__main__":
    unittest.main()
