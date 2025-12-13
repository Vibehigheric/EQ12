import argparse
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import List, Tuple

from markdown_it import MarkdownIt
from rich.console import Console
from rich.table import Table

console = Console()

DB_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS docs USING fts5(
    path UNINDEXED,
    heading,
    content,
    score,
    mtime UNINDEXED,
    tokenize = 'porter'
);
"""

# Keywords that indicate "upgrade / performance / TODO" relevance
UPGRADE_KEYWORDS = [
    "upgrade", "update", "migrate", "migration", "deprecated", "deprecate",
    "refactor", "optimize", "optimization", "performance", "latency",
    "throughput", "bottleneck", "profiling", "scale", "scalability",
    "gpu", "tpu", "coral", "cuda", "driver", "firmware", "kernel",
    "wsl", "docker", "compose", "cluster", "swarm",
    "security", "hardening", "patch", "cve",
]

TODO_MARKERS = [
    "todo", "fixme", "xxx", "hack", "note:", "later:", "next step", "future work"
]

KEYWORD_REGEX = re.compile(
    r"(" + "|".join(re.escape(k) for k in UPGRADE_KEYWORDS + TODO_MARKERS) + r")",
    re.IGNORECASE,
)


def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(DB_SCHEMA)
    return conn


def chunk_markdown(path: Path) -> List[Tuple[str, str]]:
    """
    Parse markdown into (heading, chunk_text) pairs.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    md = MarkdownIt()
    tokens = md.parse(text)

    chunks = []
    current_heading = ""
    current_lines: List[str] = []

    for token in tokens:
        if token.type == "heading_open":
            # flush previous chunk
            if current_lines:
                chunks.append((current_heading, "\n".join(current_lines).strip()))
                current_lines = []

        if token.type == "inline":
            if token.map and token.content:
                if token.level == 1 and token.content.strip():
                    # Probably a heading inline
                    current_heading = token.content.strip()
                else:
                    current_lines.append(token.content)

    if current_lines:
        chunks.append((current_heading, "\n".join(current_lines).strip()))

    # If no headings detected, treat whole file as one chunk
    if not chunks:
        chunks = [("", text)]

    return chunks


def score_chunk(content: str) -> int:
    """
    Simple scoring based on occurrences of our keywords.
    """
    matches = KEYWORD_REGEX.findall(content)
    return len(matches)


def index_directory(db_path: Path, root: Path, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {".git", ".venv", "node_modules", "__pycache__"}

    conn = open_db(db_path)
    cur = conn.cursor()

    console.print(f"[bold cyan]Indexing markdown under[/] {root} ...")

    # Clear old index
    cur.execute("DELETE FROM docs;")
    conn.commit()

    count = 0
    start_time = time.time()

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter dirs
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for name in filenames:
            if not name.lower().endswith(".md"):
                continue

            full_path = Path(dirpath) / name
            try:
                mtime = full_path.stat().st_mtime
            except OSError:
                continue

            rel_path = str(full_path.relative_to(root))

            try:
                chunks = chunk_markdown(full_path)
            except Exception as e:
                console.print(f"[red]Failed to parse {full_path}: {e}[/red]")
                continue

            for heading, content in chunks:
                if not content.strip():
                    continue

                sc = score_chunk(content)
                if sc == 0:
                    continue  # only index relevant stuff

                cur.execute(
                    "INSERT INTO docs (path, heading, content, score, mtime) VALUES (?, ?, ?, ?, ?);",
                    (rel_path, heading, content, sc, mtime),
                )
                count += 1

    conn.commit()
    elapsed = time.time() - start_time
    console.print(f"[green]Indexed {count} relevant chunks in {elapsed:.2f}s[/green]")
    conn.close()


def search_db(db_path: Path, query: str, limit: int = 20):
    conn = open_db(db_path)
    cur = conn.cursor()

    sql = """
    SELECT path, heading, snippet(docs, 2, '[', ']', '...', 10), score
    FROM docs
    WHERE docs MATCH ?
    ORDER BY score DESC
    LIMIT ?;
    """
    rows = cur.execute(sql, (query, limit)).fetchall()

    table = Table(title=f"Search results for: {query}")
    table.add_column("Score", style="magenta", justify="right")
    table.add_column("File")
    table.add_column("Heading")
    table.add_column("Snippet")

    for path, heading, snippet_text, score in rows:
        table.add_row(str(score), path, heading or "-", snippet_text)

    console.print(table)
    conn.close()


def hotlist(db_path: Path, limit: int = 20):
    conn = open_db(db_path)
    cur = conn.cursor()

    sql = """
    SELECT path, heading, substr(content, 1, 200), score
    FROM docs
    ORDER BY score DESC, mtime DESC
    LIMIT ?;
    """
    rows = cur.execute(sql, (limit,)).fetchall()

    table = Table(title="Top upgrade/performance/TODO hotspots")
    table.add_column("Score", style="magenta", justify="right")
    table.add_column("File")
    table.add_column("Heading")
    table.add_column("Snippet")

    for path, heading, snippet_text, score in rows:
        table.add_row(str(score), path, heading or "-", snippet_text.replace("\n", " "))

    console.print(table)
    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Markdown Upgrade/Performance/TODO scanner and searcher"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("mdscan_index.sqlite"),
        help="Path to SQLite index file",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Index markdown files")
    p_index.add_argument(
        "root", type=Path, help="Root directory to scan for .md files"
    )

    p_search = sub.add_parser("search", help="Search indexed markdown")
    p_search.add_argument("query", type=str, help="FTS query string")
    p_search.add_argument("--limit", type=int, default=20)

    p_hot = sub.add_parser("hotlist", help="Show highest-priority upgrade/TODO chunks")
    p_hot.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()

    if args.command == "index":
        index_directory(args.db, args.root)
    elif args.command == "search":
        search_db(args.db, args.query, args.limit)
    elif args.command == "hotlist":
        hotlist(args.db, args.limit)


if __name__ == "__main__":
    main()
