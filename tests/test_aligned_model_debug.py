import json
import os

from scripts.aligned_model import AlignedModel


def test_simulate_debug_loop_writes_snapshot(tmp_path, monkeypatch) -> None:
    # Arrange
    logs_dir = tmp_path / "logs"
    monkeypatch.setenv("EQ12_LOGS", str(logs_dir))

    principles = {"AS1": "No covert actions or strategic deception."}
    model = AlignedModel("test", principles)

    # Act
    success, message, snapshot_path = model._simulate_debug_loop(
        "fix failing tests", max_iterations=2
    )

    # Assert
    assert isinstance(success, bool)
    assert isinstance(message, str)
    assert os.path.exists(snapshot_path)

    with open(snapshot_path, encoding="utf-8") as f:
        try:
            obj = json.load(f)

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON from {file_path}: {e}")

            raise

        except FileNotFoundError as e:
            logging.error(f"JSON file not found: {e}")

            raise
    assert "tag" in obj
    assert "data" in obj
    assert "history" in obj["data"]
