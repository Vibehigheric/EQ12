from __future__ import annotations

import logging

from src.client import ChatGPTClient

from src.utils import format_response


def main():
    logging.basicConfig(level=logging.INFO)
    client = ChatGPTClient()  # loads API key from env/config if available

    try:
        while True:
            user = input().strip()
            if not user or user.lower() == "exit":
                break

            # keep simple: any non-empty line is sent to the API
            response = client.get_response(user)
            logger.info(format_response(response))
    except (KeyboardInterrupt, EOFError):
        print()
    # return for test harnesses
    return


if __name__ == "__main__":
    main()
