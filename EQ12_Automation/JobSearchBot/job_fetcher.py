from datetime import datetime
from typing import Any

import requests


def _annualize(hourly: float) -> float:
    return hourly * 2080.0


def fetch_jobs_multi(
    adzuna_app_id: str,
    adzuna_app_key: str,
    keywords: list[str],
    locations: list[str],
    min_hourly: float,
    results_per_page: int = 25,
) -> list[dict[str, Any]]:
    all_jobs = []
    base_url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    min_salary_annual = _annualize(min_hourly)

    for loc in locations:
        for kw in keywords:
            params = {
                "app_id": adzuna_app_id,
                "app_key": adzuna_app_key,
                "results_per_page": results_per_page,
                "what": kw,
                "where": loc,
                "salary_min": int(min_salary_annual),
                "sort_by": "salary",
            }
            try:
                resp = requests.get(base_url, params=params, timeout=15)
                data = resp.json() if resp.ok else {}
                results = data.get("results", [])
                all_jobs.extend(results)
            except Exception:
                continue
    return all_jobs


def normalize_and_filter(jobs: list[dict[str, Any]], min_hourly: float) -> list[dict[str, Any]]:
    min_annual = 2080 * min_hourly
    seen = set()
    cleaned = []
    for j in jobs:
        title = j.get("title", "").strip()
        company = (j.get("company") or {}).get("display_name") or "Unknown"
        location = (j.get("location") or {}).get("display_name") or ""
        url = j.get("redirect_url") or j.get("adref") or ""
        salary_min = j.get("salary_min") or 0
        salary_max = j.get("salary_max") or salary_min
        try:
            salary_min = float(salary_min or 0)
        except Exception:
            salary_min = 0.0
        if salary_min < min_annual:
            continue
        if not url or url in seen:
            continue
        seen.add(url)
        cleaned.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "url": url,
                "created": j.get("created", ""),
                "description": j.get("description", ""),
            }
        )
    cleaned.sort(key=lambda x: x.get("salary_min", 0), reverse=True)
    return cleaned


def format_for_email(items: list[dict[str, Any]]) -> str:
    lines = []
    for it in items:
        sal = f"${int(it['salary_min']):,}/yr" if it.get("salary_min") else "N/A"
        created = it.get("created") or ""
        if created:
            try:
                created = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime(
                    "%Y-%m-%d"
                )
            except Exception:
                pass
        line = f"{it['title']} @ {it['company']} | {it['location']} | {sal}\n{it['url']}"
        if created:
            line += f"\nPosted: {created}"
        lines.append(line)
    return "\n\n".join(lines)


def format_for_telegram(items: list[dict[str, Any]], limit: int = 10) -> str:
    if not items:
        return "No $40/hr+ matches found today."
    top = items[:limit]
    msg_lines = [f"🔥 $40+/hr Job Matches (Top {len(top)}/{len(items)}):"]
    for it in top:
        sal = f"${int(it['salary_min']):,}/yr" if it.get("salary_min") else "N/A"
        msg_lines.append(f"• {it['title']} @ {it['company']} — {sal}\n{it['url']}")
    return "\n".join(msg_lines)
