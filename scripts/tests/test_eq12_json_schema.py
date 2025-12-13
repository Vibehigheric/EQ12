import json
import os

import pytest


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "logfile,required_keys",
    [
        ("C:/EQ12/logs/stocks_latest.json", ["results"]),
        ("C:/EQ12/logs/crypto_latest.json", ["results"]),
        ("C:/EQ12/logs/odds_sports.json", ["sports", "odds"]),
        ("C:/EQ12/logs/jobs_controltech.json", ["jobs"]),
        ("C:/EQ12/logs/recycle_report.json", ["recycle"]),
    ],
)
def test_json_schema(logfile, required_keys) -> None:
    assert os.path.exists(logfile), f"Missing log file: {logfile}"
    data = load_json(logfile)
    for key in required_keys:
        assert key in data, f"Missing key '{key}' in {logfile}"
