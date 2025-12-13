# eq12_vector_service.py
from __future__ import annotations

import json
import math
import os

try:
    from openai import OpenAI

    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None

STORE = os.path.join(os.getcwd(), "data", "vector_store.json")


def _load() -> list[dict]:
    if not os.path.exists(STORE):
        return []
    with open(STORE, encoding="utf-8") as f:
        return json.load(f)


def _save(rows: list[dict]):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def embed(texts: list[str]) -> list[list[float]]:
    assert _client, "OpenAI client not initialized for embeddings"
    resp = _client.embeddings.create(
        model=os.getenv("EQ12_EMBED_MODEL", "text-embedding-3-small"), input=texts
    )
    return [d.embedding for d in resp.data]


def upsert(docs: list[dict]):
    """
    docs: [{"id": str, "text": str, "meta": dict}]
    """
    rows = _load()
    texts = [d["text"] for d in docs]
    vecs = embed(texts)
    for d, v in zip(docs, vecs, strict=False):
        rows = [r for r in rows if r["id"] != d["id"]]
        rows.append({"id": d["id"], "text": d["text"], "meta": d.get("meta", {}), "vec": v})
    _save(rows)


def _cos(a, b):
    num = sum(x * y for x, y in zip(a, b, strict=False))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(y * y for y in b))
    return 0 if (da == 0 or db == 0) else num / (da * db)


def search(query: str, k: int = 8) -> list[dict]:
    rows = _load()
    if not rows:
        return []
    qv = embed([query])[0]
    scored = sorted(rows, key=lambda r: _cos(qv, r["vec"]), reverse=True)
    return [{"id": r["id"], "text": r["text"], "meta": r["meta"]} for r in scored[:k]]
