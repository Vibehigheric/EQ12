import json
import os


def test_stocks_json_schema() -> None:
    path = os.path.expandvars(r"C:/EQ12/logs/stocks_latest.json")
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON from {file_path}: {e}")

            raise

        except FileNotFoundError as e:
            logging.error(f"JSON file not found: {e}")

            raise
    # Top-level keys
    for key in ("type", "ts", "tickers", "results"):
        assert key in data, f"Missing key: {key}"
    assert isinstance(data["results"], list), "results must be a list"
    required = {"ticker", "close", "ema20", "ema50", "rsi14", "mom5", "signal"}
    for i, r in enumerate(data["results"]):
        missing = required - r.keys()
        assert not missing, f"Result {i} missing keys: {missing}"
