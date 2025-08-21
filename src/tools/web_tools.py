import requests
from typing import List
from langchain_core.tools import tool

WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"

_CALLS_GUARD = {"count": 0, "limit": 3}  


@tool("wiki_search")
def wiki_search(query: str, max_results: int = 2, lang: str = "en") -> str:
    """
    Deterministic Wikipedia search + summary (language default: en).
    Guarded to avoid tool call loops. Returns compact summaries.
    """
    if _CALLS_GUARD["count"] >= _CALLS_GUARD["limit"]:
        return "tool_guard: limit reached"

    _CALLS_GUARD["count"] += 1

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": max_results,
    }
    r = requests.get(WIKI_SEARCH_URL, params=params, timeout=20)
    r.raise_for_status()
    data = r.json().get("query", {}).get("search", [])
    if not data:
        return "no_results"

    results: List[str] = []
    for item in data[:max_results]:
        title = item.get("title")
        if not title:
            continue
        s = requests.get(WIKI_SUMMARY_URL.format(title), timeout=20, headers={"accept-language": lang})
        if s.status_code == 200:
            j = s.json()
            extract = j.get("extract") or ""
            description = j.get("description") or ""
            results.append(f"{title}: {description} — {extract[:400]}")

    return "\n\n".join(results) if results else "no_summaries"
