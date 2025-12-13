import os
import time

import requests

DEFAULT_TIMEOUT = 20
RETRY_BACKOFF = [0.5, 1.0, 2.0]


def _request_with_retries(method: str, url: str, **kwargs):
    last_exc = None
    for _i, delay in enumerate([0.0, *RETRY_BACKOFF]):
        if delay:
            time.sleep(delay)
        try:
            resp = requests.request(
                method, url, timeout=kwargs.pop("timeout", DEFAULT_TIMEOUT), **kwargs
            )
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_exc = e
    raise last_exc


class BingClient:
    def __init__(self, api_key: str | None = None, endpoint: str | None = None):
        self.api_key = api_key or os.getenv("BING_KEY")
        self.endpoint = endpoint or os.getenv(
            "BING_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search"
        )
        self.news_endpoint = os.getenv(
            "BING_NEWS_ENDPOINT", "https://api.bing.microsoft.com/v7.0/news/search"
        )
        self.image_endpoint = os.getenv(
            "BING_IMAGE_ENDPOINT", "https://api.bing.microsoft.com/v7.0/images/search"
        )
        self.suggest_endpoint = os.getenv(
            "BING_SUGGEST_ENDPOINT", "https://api.bing.microsoft.com/v7.0/Suggestions"
        )
        if not self.api_key:
            raise ValueError("BingClient: missing API key (set BING_KEY).")

    def web_search(self, query: str, count: int = 10) -> list[dict]:
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": count,
            "textDecorations": False,
            "textFormat": "Raw",
        }
        js = _request_with_retries("GET", self.endpoint, headers=headers, params=params).json()
        out = []
        for item in js.get("webPages", {}).get("value", []):
            out.append(
                {
                    "title": item.get("name"),
                    "url": item.get("url"),
                    "snippet": item.get("snippet"),
                    "source": "bing",
                    "published_at": item.get("dateLastCrawled"),
                }
            )
        return out

    def news_search(self, query: str, count: int = 10, freshness: str | None = None) -> list[dict]:
        # freshness: "Day", "Week", "Month"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query, "count": count}
        if freshness:
            params["freshness"] = freshness
        js = _request_with_retries("GET", self.news_endpoint, headers=headers, params=params).json()
        out = []
        for item in js.get("value", []):
            out.append(
                {
                    "title": item.get("name"),
                    "url": item.get("url"),
                    "snippet": item.get("description"),
                    "source": "bing_news",
                    "published_at": item.get("datePublished"),
                }
            )
        return out

    def autosuggest(self, query: str) -> list[str]:
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query}
        js = _request_with_retries(
            "GET", self.suggest_endpoint, headers=headers, params=params
        ).json()
        texts = []
        for group in js.get("suggestionGroups", []):
            for s in group.get("searchSuggestions", []):
                if s.get("displayText"):
                    texts.append(s["displayText"])
        return texts


class GoogleClient:
    def __init__(self, api_key: str | None = None, cse_id: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_KEY")
        self.cse_id = cse_id or os.getenv("GOOGLE_CSE_ID")
        if not self.api_key:
            raise ValueError("GoogleClient: missing API key (set GOOGLE_KEY).")
        if not self.cse_id:
            raise ValueError("GoogleClient: missing CSE ID (set GOOGLE_CSE_ID).")

    def web_search(self, query: str, count: int = 10) -> list[dict]:
        endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(count, 10),
        }
        js = _request_with_retries("GET", endpoint, params=params).json()
        out = []
        for item in js.get("items", []) or []:
            out.append(
                {
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "snippet": item.get("snippet"),
                    "source": "google",
                    "published_at": None,
                }
            )
        return out
