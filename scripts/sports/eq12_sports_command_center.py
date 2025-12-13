"""EQ12 Sports Command Center

Provides data pipelines, seasonal context, and betting edge distribution for all major sports.
Integrates with existing EQ12 logging conventions and environment variable configuration.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import pytz
import requests

REPO_ROOT = Path(os.environ.get("EQ12_REPO_ROOT", Path(__file__).resolve().parents[2]))
LOG_ROOT = Path(os.environ.get("EQ12_LOG_ROOT", REPO_ROOT / "logs" / "sports"))
DATA_ROOT = Path(os.environ.get("EQ12_DATA_ROOT", REPO_ROOT / "data"))
CONFIG_ROOT = Path(os.environ.get("EQ12_CONFIG_ROOT", REPO_ROOT / "configs"))

SEASON_CLOCK_FILE = CONFIG_ROOT / "sports_season_clock.json"
KEYWORD_FILE = CONFIG_ROOT / "sports_keywords.txt"
EDGE_OUTPUT = DATA_ROOT / "sports_edges.json"

DEFAULT_SPORTS = [
    "NFL",
    "NBA",
    "MLB",
    "NHL",
    "MLS",
    "EPL",
    "LaLiga",
    "SerieA",
    "UCL",
    "NCAAF",
    "NCAAB",
]


@dataclass
class SeasonWindow:
    sport: str
    preseason_start: dt.date
    regular_start: dt.date
    playoffs_start: dt.date
    season_end: dt.date

    @classmethod
    def from_dict(cls, sport: str, payload: dict[str, str]) -> SeasonWindow:
        return cls(
            sport=sport,
            preseason_start=dt.date.fromisoformat(payload["preseason_start"]),
            regular_start=dt.date.fromisoformat(payload["regular_start"]),
            playoffs_start=dt.date.fromisoformat(payload["playoffs_start"]),
            season_end=dt.date.fromisoformat(payload["season_end"]),
        )

    def phase(self, current_date: dt.date) -> str:
        if current_date < self.preseason_start:
            return "offseason"
        if current_date < self.regular_start:
            return "preseason"
        if current_date < self.playoffs_start:
            return "regular"
        if current_date <= self.season_end:
            return "playoffs"
        return "offseason"


@dataclass
class EdgeSignal:
    sport: str
    event_id: str
    event_time: str
    market: str
    side: str
    edge_value: float
    confidence: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "sport": self.sport,
            "event_id": self.event_id,
            "event_time": self.event_time,
            "market": self.market,
            "side": self.side,
            "edge_value": self.edge_value,
            "confidence": self.confidence,
            "notes": self.notes,
        }


class SportsCommandCenter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.session = requests.Session()
        self.tz = pytz.timezone(args.timezone)
        LOG_ROOT.mkdir(parents=True, exist_ok=True)
        DATA_ROOT.mkdir(parents=True, exist_ok=True)

    async def run(self) -> None:
        if self.args.refresh_calendar:
            self.refresh_season_clock()
        odds_payload = await asyncio.to_thread(self.collect_odds_sources)
        injuries = await asyncio.to_thread(self.collect_injury_reports)
        sentiment = await asyncio.to_thread(self.collect_social_sentiment)
        edges = self.generate_edges(odds_payload, injuries, sentiment)
        self.write_edges(edges)
        if self.args.dump:
            print(json.dumps([edge.to_dict() for edge in edges], indent=2))

    def refresh_season_clock(self) -> None:
        if not SEASON_CLOCK_FILE.exists():
            self.write_default_season_clock()
            self.log("Generated default season clock.")
            return
        payload = json.loads(SEASON_CLOCK_FILE.read_text())
        updated: dict[str, dict[str, str]] = {}
        for sport, body in payload.items():
            updated[sport] = {
                key: dt.date.fromisoformat(value).replace(year=dt.date.today().year).isoformat()
                for key, value in body.items()
            }
        SEASON_CLOCK_FILE.write_text(json.dumps(updated, indent=2))
        self.log("Season clock refreshed with current year context.")

    def collect_odds_sources(self) -> dict[str, object]:
        odds_api_key = os.environ.get("ODDS_API_KEY")
        payload: dict[str, object] = {}
        if not odds_api_key:
            self.log("ODDS_API_KEY missing; using placeholder odds feed.")
            for sport in self.args.sports:
                payload[sport] = {
                    "timestamp": dt.datetime.now(self.tz).isoformat(),
                    "lines": [{"event": "placeholder", "price": -110, "book": "demo"}],
                }
            return payload

        endpoint = "https://api.the-odds-api.com/v4/sports"
        try:
            sports_resp = self.session.get(
                endpoint,
                params={"apiKey": odds_api_key, "all": "true"},
                timeout=10,
            )
            sports_resp.raise_for_status()
            available = {item["key"]: item for item in sports_resp.json()}
            for sport in self.args.sports:
                sport_key = self.remap_sport_key(sport, available)
                if not sport_key:
                    continue
                lines_resp = self.session.get(
                    f"{endpoint}/{sport_key}/odds",
                    params={
                        "apiKey": odds_api_key,
                        "regions": "us,eu",
                        "markets": "h2h,spreads,totals",
                        "oddsFormat": "american",
                    },
                    timeout=10,
                )
                if lines_resp.ok:
                    payload[sport] = lines_resp.json()
        except requests.RequestException as exc:
            self.log(f"Odds API failure: {exc}")
        return payload

    def collect_injury_reports(self) -> dict[str, object]:
        injuries_path = DATA_ROOT / "injuries.json"
        if injuries_path.exists():
            try:
                return json.loads(injuries_path.read_text())
            except json.JSONDecodeError:
                self.log("Unable to parse existing injuries.json; ignoring.")
        return {"timestamp": dt.datetime.now(self.tz).isoformat(), "entries": []}

    def collect_social_sentiment(self) -> dict[str, object]:
        bearer = os.environ.get("X_BEARER_TOKEN")
        if not bearer:
            self.log("X_BEARER_TOKEN missing; sentiment disabled.")
            return {"tweets": []}
        queries = self.build_sentiment_queries()
        tweets: list[dict[str, str]] = []
        for query in queries:
            try:
                resp = self.session.get(
                    "https://api.x.com/2/tweets/search/recent",
                    params={
                        "query": query,
                        "max_results": 50,
                        "tweet.fields": "created_at,author_id",
                    },
                    headers={"Authorization": f"Bearer {bearer}"},
                    timeout=10,
                )
                if resp.ok and "data" in resp.json():
                    tweets.extend(resp.json()["data"])
            except requests.RequestException as exc:
                self.log(f"Sentiment fetch failed for query {query}: {exc}")
        return {"timestamp": dt.datetime.now(self.tz).isoformat(), "tweets": tweets}

    def generate_edges(
        self,
        odds_payload: dict[str, object],
        injuries: dict[str, object],
        sentiment: dict[str, object],
    ) -> list[EdgeSignal]:
        season_clock = self.load_season_clock()
        current_date = dt.datetime.now(self.tz).date()
        injuries_index = self.index_injuries(injuries)
        sentiment_score = self.compute_sentiment(sentiment)

        edges: list[EdgeSignal] = []
        for sport, _odds in odds_payload.items():
            phase = season_clock.get(
                sport,
                SeasonWindow(
                    sport,
                    current_date,
                    current_date,
                    current_date,
                    current_date,
                ),
            ).phase(current_date)
            adjustments = self.compute_phase_adjustment(phase)
            injury_penalty = injuries_index.get(sport, 0.0)
            confidence = max(0.0, 1.0 - injury_penalty)
            base_edge = 0.5 + adjustments + sentiment_score.get(sport, 0.0)
            edge_signal = EdgeSignal(
                sport=sport,
                event_id=f"{sport}-auto",
                event_time=dt.datetime.now(self.tz).isoformat(),
                market="spread",
                side="auto-edge",
                edge_value=round(base_edge, 3),
                confidence=round(min(1.0, confidence), 3),
                notes=[
                    f"phase={phase}",
                    f"injury_penalty={injury_penalty:.2f}",
                    f"sentiment={sentiment_score.get(sport, 0.0):.2f}",
                ],
            )
            edges.append(edge_signal)
        return edges

    def log(self, message: str) -> None:
        timestamp = dt.datetime.now(self.tz).isoformat()
        LOG_ROOT.mkdir(parents=True, exist_ok=True)
        logfile = LOG_ROOT / "sports_command_center.log"
        with logfile.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message}\n")

    def load_season_clock(self) -> dict[str, SeasonWindow]:
        if not SEASON_CLOCK_FILE.exists():
            self.write_default_season_clock()
        try:
            payload = json.loads(SEASON_CLOCK_FILE.read_text())
            return {sport: SeasonWindow.from_dict(sport, data) for sport, data in payload.items()}
        except json.JSONDecodeError:
            self.log("Invalid season clock file; regenerating defaults.")
            self.write_default_season_clock()
            return self.load_season_clock()

    def write_default_season_clock(self) -> None:
        defaults = {
            sport: {
                "preseason_start": f"{dt.date.today().year}-07-15",
                "regular_start": f"{dt.date.today().year}-09-01",
                "playoffs_start": f"{dt.date.today().year}-12-01",
                "season_end": f"{dt.date.today().year + 1}-02-15",
            }
            for sport in DEFAULT_SPORTS
        }
        SEASON_CLOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        SEASON_CLOCK_FILE.write_text(json.dumps(defaults, indent=2))

    def write_edges(self, edges: list[EdgeSignal]) -> None:
        EDGE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        EDGE_OUTPUT.write_text(json.dumps([edge.to_dict() for edge in edges], indent=2))

    def compute_phase_adjustment(self, phase: str) -> float:
        return {
            "preseason": -0.15,
            "regular": 0.0,
            "playoffs": 0.2,
            "offseason": -0.5,
        }.get(phase, 0.0)

    def index_injuries(self, injuries: dict[str, object]) -> dict[str, float]:
        penalties: dict[str, float] = {}
        entries = injuries.get("entries", []) if isinstance(injuries, dict) else []
        for entry in entries:
            sport = entry.get("sport")
            severity = entry.get("severity", 0.1)
            if sport:
                penalties[sport] = penalties.get(sport, 0.0) + float(severity)
        return {sport: min(1.0, value) for sport, value in penalties.items()}

    def compute_sentiment(self, sentiment: dict[str, object]) -> dict[str, float]:
        tweets = sentiment.get("tweets", []) if isinstance(sentiment, dict) else []
        scores: dict[str, float] = {}
        for tweet in tweets:
            text = tweet.get("text", "").lower()
            for sport in self.args.sports:
                if sport.lower() in text:
                    scores[sport] = scores.get(sport, 0.0) + 0.01
        return scores

    def build_sentiment_queries(self) -> list[str]:
        keywords = self.load_keywords()
        queries: list[str] = []
        for chunk in self.chunk_keywords(keywords, 10):
            queries.append("(" + " OR ".join(chunk) + ") lang:en -is:retweet")
        return queries

    def load_keywords(self) -> list[str]:
        if KEYWORD_FILE.exists():
            return [line.strip() for line in KEYWORD_FILE.read_text().splitlines() if line.strip()]
        KEYWORD_FILE.write_text("\\n".join(DEFAULT_SPORTS))
        return DEFAULT_SPORTS

    @staticmethod
    def chunk_keywords(keywords: list[str], size: int) -> list[list[str]]:
        return [keywords[i : i + size] for i in range(0, len(keywords), size)]

    @staticmethod
    def remap_sport_key(sport: str, available: dict[str, object]) -> str | None:
        overrides = {
            "NFL": "americanfootball_nfl",
            "NBA": "basketball_nba",
            "MLB": "baseball_mlb",
            "NHL": "icehockey_nhl",
            "EPL": "soccer_epl",
            "LaLiga": "soccer_spain_la_liga",
            "SerieA": "soccer_italy_serie_a",
            "UCL": "soccer_uefa_champions_league",
            "NCAA": "americanfootball_ncaaf",
            "NCAAB": "basketball_ncaab",
        }
        candidate = overrides.get(sport, sport.lower())
        if candidate in available:
            return candidate
        for key in available:
            if sport.lower() in key:
                return key
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EQ12 Sports Command Center")
    parser.add_argument("--sports", nargs="*", default=DEFAULT_SPORTS, help="Sports to include")
    parser.add_argument("--timezone", default="US/Eastern", help="Timezone for scheduling")
    parser.add_argument("--refresh-calendar", action="store_true", dest="refresh_calendar")
    parser.add_argument("--dump", action="store_true", help="Print edges to stdout")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    center = SportsCommandCenter(args)
    asyncio.run(center.run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
