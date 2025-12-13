import json
import sys
from pathlib import Path

# Ensure project root is importable
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from scripts.rakuten_scraper import RakutenConfig, RakutenScraper


def test_rakuten_dry_run(tmp_path) -> None:
    out = tmp_path / "rakuten.json"
    cfg = RakutenConfig(dry_run=True, out=str(out))
    s = RakutenScraper(cfg)
    s.run()
    # dry-run should not create file
    assert not out.exists()


def test_rakuten_write(tmp_path) -> None:
    out = tmp_path / "rakuten.json"
    cfg = RakutenConfig(dry_run=False, out=str(out))
    s = RakutenScraper(cfg)
    s.run()
    assert out.exists()
    try:
        data = json.loads(out.read_text())

    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON string: {e}")

        data = {}  # Safe fallback)
    assert isinstance(data, list)
