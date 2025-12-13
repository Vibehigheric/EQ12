import json
import sys
from pathlib import Path

# ensure project root
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from scripts.cf_rewards_scraper import load_watchlist, process_watchlist, save_results


def test_load_coupon_watchlist() -> None:
    wl = load_watchlist("configs/coupon_watchlist.json")
    assert isinstance(wl, list)


def test_process_and_save(tmp_path) -> None:
    wl = load_watchlist("configs/coupon_watchlist.json")
    results = process_watchlist(wl)
    out = tmp_path / "coupons.json"
    save_results(results, str(out), dry_run=False)
    assert out.exists()
    try:
        data = json.loads(out.read_text())

    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON string: {e}")

        data = {}  # Safe fallback)
    assert isinstance(data, list)
