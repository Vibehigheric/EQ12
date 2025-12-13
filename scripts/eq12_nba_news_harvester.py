# C:\EQ12\scripts\eq12_nba_news_harvester.py
# EQ12 NBA News/RSS Harvester: correlates headlines with your bets and flags availability/injury items.

import os, re, json, glob, time, hashlib, html
import argparse
from datetime import datetime, timezone
from collections import defaultdict
from urllib.parse import urlparse

# Third-party deps: pip install feedparser python-slugify python-dateutil
import feedparser
import requests

# --------- CONFIG DEFAULTS ---------
DEFAULT_FEEDS = [
    # Known-working NBA/Sports RSS feeds (edit/extend as you like)
    "https://www.espn.com/espn/rss/nba/news",
    "https://www.cbssports.com/rss/headlines/nba/",
    "https://sports.yahoo.com/nba/rss/",
    "https://www.rotowire.com/rss/news.php?sport=NBA",
    "https://basketball.realgm.com/rss/wiretap/0/0.xml",
    "https://www.hoopsrumors.com/feed",
]

KEYWORDS_INJURY = [
    "out", "questionable", "doubtful", "ruled out",
    "game-time decision", "minutes limit", "probable",
    "inactive", "status", "injury", "return", "ankle",
    "hamstring", "knee", "illness", "back-to-back", "rest"
]

KEYWORDS_MARKET_MOVE = [
    "upgrade", "downgrade", "starting", "benched", "lineup",
    "trade", "suspension", "signed", "waived"
]

REPORT_DIR = r"C:\EQ12\reports"
LOGS_DIR   = r"C:\EQ12\logs"
CACHE_DIR  = r"C:\EQ12\cache"
WORKSPACE  = r"C:\EQ12"
SGP_GLOB   = os.path.join(LOGS_DIR, "clean_sgp_data_*.json")  # your roster-validated SGP JSONs

TELEGRAM_ENV = os.path.join(WORKSPACE, "coral_betting_ai", "coral_config.env")  # already in your stack

# --------- UTILS ---------
def now_utc_iso():
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

def safe_mkdir(p):
    os.makedirs(p, exist_ok=True)

def hash_str(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()[:16]

def load_yaml_optional(yaml_path: str):
    try:
        import yaml  # optional
    except Exception:
        return None
    if not os.path.exists(yaml_path):
        return None
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_latest_bets_json() -> dict:
    files = sorted(glob.glob(SGP_GLOB), reverse=True)
    if not files:
        return {}
    try:
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def extract_players_teams_from_bets(bets_data: dict):
    players = set()
    teams   = set()
    # Assume your JSON looks like the example you produced. We'll scan all leg fields as text.
    def add_from_text(txt: str):
        if not txt: return
        # crude extraction: Names (Two Capitalized Words) + all-upper team tokens like LAL, BOS, etc.
        for m in re.findall(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", txt):
            players.add(m.strip())
        for m in re.findall(r"\b[A-Z]{2,4}\b", txt):
            teams.add(m.strip())

    if isinstance(bets_data, dict):
        text_blob = json.dumps(bets_data, ensure_ascii=False)
        add_from_text(text_blob)

    # Manual seed with common NBA team codes you might see in your SGPs:
    # (If you already embed team codes in your JSON, this will capture them.)
    return sorted(players), sorted(teams)

def fetch_feeds(feed_list):
    entries = []
    for url in feed_list:
        try:
            d = feedparser.parse(url)
            for e in d.entries:
                title = html.unescape(getattr(e, "title", "") or "")
                summary = html.unescape(getattr(e, "summary", "") or "")
                link = getattr(e, "link", "")
                published = getattr(e, "published", getattr(e, "updated", "")) or ""
                entries.append({
                    "feed": url,
                    "title": title.strip(),
                    "summary": re.sub(r"<[^>]+>", " ", summary).strip(),
                    "link": link,
                    "published": published
                })
        except Exception as ex:
            entries.append({
                "feed": url, "title": f"[FEED ERROR] {url}",
                "summary": str(ex), "link": "", "published": ""
            })
    return entries

def score_entry(entry, players, teams):
    text = f"{entry['title']} {entry['summary']}".lower()
    score = 0
    hits = {"players": [], "teams": [], "injury_terms": [], "market_terms": []}

    # players
    for p in players:
        p_low = p.lower()
        if p_low in text:
            hits["players"].append(p)
            score += 5

    # teams
    for t in teams:
        t_low = t.lower()
        if t_low in text:
            hits["teams"].append(t)
            score += 3

    # injury & market move terms
    for k in KEYWORDS_INJURY:
        if re.search(rf"\b{k}\b", text):
            hits["injury_terms"].append(k)
            score += 2

    for k in KEYWORDS_MARKET_MOVE:
        if re.search(rf"\b{k}\b", text):
            hits["market_terms"].append(k)
            score += 1

    # boost if both player and injury keyword present
    if hits["players"] and hits["injury_terms"]:
        score += 4

    return score, hits

def dedupe(entries):
    seen = set()
    out = []
    for e in entries:
        key = hash_str((e.get("title","") + "|" + e.get("link","")).strip())
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out

def load_telegram_creds():
    if not os.path.exists(TELEGRAM_ENV):
        return None, None
    token, chat_id = None, None
    with open(TELEGRAM_ENV, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                token = line.split("=",1)[1].strip()
            if line.startswith("TELEGRAM_CHAT_ID="):
                chat_id = line.split("=",1)[1].strip()
    return token, chat_id

def telegram_send(text: str):
    token, chat_id = load_telegram_creds()
    if not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True}, timeout=10)
        return resp.ok
    except Exception:
        return False

# --------- MAIN ---------
def main():
    parser = argparse.ArgumentParser(description="EQ12 NBA RSS Harvester")
    parser.add_argument("--workspace", default=WORKSPACE)
    parser.add_argument("--feeds-yaml", default=os.path.join(WORKSPACE, "configs", "nba_feeds.yaml"),
                        help="Optional YAML with list: feeds: [ ... ]")
    parser.add_argument("--top-n", type=int, default=60, help="How many top-scored items to keep")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary to Telegram")
    args = parser.parse_args()

    safe_mkdir(REPORT_DIR)
    safe_mkdir(LOGS_DIR)
    safe_mkdir(CACHE_DIR)

    # Load feeds
    feeds_cfg = load_yaml_optional(args.feeds_yaml)
    if feeds_cfg and isinstance(feeds_cfg.get("feeds"), list) and feeds_cfg["feeds"]:
        feed_list = feeds_cfg["feeds"]
    else:
        feed_list = DEFAULT_FEEDS

    # Load latest bets for entity extraction
    bets = load_latest_bets_json()
    players, teams = extract_players_teams_from_bets(bets)

    # Fetch + score
    raw_entries = fetch_feeds(feed_list)
    raw_entries = dedupe(raw_entries)

    scored = []
    for e in raw_entries:
        s, hits = score_entry(e, players, teams)
        e2 = dict(e)
        e2["score"] = int(s)
        e2["hits"] = hits
        scored.append(e2)

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[: args.top_n]

    # Build markdown
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    md_path = os.path.join(REPORT_DIR, f"nba_news_{ts}.md")
    json_path = os.path.join(REPORT_DIR, f"nba_news_{ts}.json")

    md = []
    md.append(f"# NBA News Correlated To Current Bets  {datetime.now().strftime('%b %d, %Y %I:%M %p')}")
    md.append("")
    md.append(f"- Items scanned: **{len(raw_entries)}**")
    md.append(f"- Showing top: **{len(top)}** by relevance to your current slate")
    md.append(f"- Players matched: {', '.join(players) if players else '(none found)'}")
    md.append(f"- Teams matched: {', '.join(teams) if teams else '(none found)'}")
    md.append("")
    md.append("---")

    for i, e in enumerate(top, 1):
        hits = e["hits"]
        badges = []
        if hits["players"]: badges.append("")
        if hits["teams"]: badges.append("")
        if hits["injury_terms"]: badges.append("")
        if hits["market_terms"]: badges.append("")
        badge_str = " ".join(badges) if badges else ""
        md.append(f"### {i}. {e['title']}  {badge_str}")
        if e.get("published"): md.append(f"*{e['published']}*")
        domain = urlparse(e.get("link","")).netloc
        if domain: md.append(f"**Source:** {domain}")
        if e.get("link"): md.append(f"[Open]({e['link']})")
        if e.get("summary"):
            cleaned = re.sub(r"\s+", " ", e["summary"]).strip()
            md.append(f"> {cleaned[:500]}{'' if len(cleaned)>500 else ''}")
        # Hits line
        hline = []
        if hits["players"]: hline.append(f"Players: {', '.join(hits['players'])}")
        if hits["teams"]: hline.append(f"Teams: {', '.join(hits['teams'])}")
        if hits["injury_terms"]: hline.append(f"Injury terms: {', '.join(sorted(set(hits['injury_terms'])))}")
        if hits["market_terms"]: hline.append(f"Market: {', '.join(sorted(set(hits['market_terms'])))}")
        if hline: md.append(f"_Match:_ " + " | ".join(hline))
        md.append(f"**Score:** {e['score']}")
        md.append("")
        md.append("---")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": now_utc_iso(),
            "players": players,
            "teams": teams,
            "feeds": feed_list,
            "results": top
        }, f, indent=2, ensure_ascii=False)

    print(f" Wrote report:\n  - {md_path}\n  - {json_path}")

    if args.send_telegram:
        # Compact Telegram summary
        lines = [f" NBA News vs Bets ({datetime.now().strftime('%m/%d %I:%M %p')})"]
        shown = 0
        for e in top:
            if shown >= 10: break
            t = e["title"]
            link = e.get("link","")
            score = e["score"]
            inj = "" if e["hits"]["injury_terms"] else ""
            lines.append(f"{inj} {t}  (Score {score})")
            if link: lines.append(link)
            shown += 1
        telegram_send("\n".join(lines))

if __name__ == "__main__":
    main()