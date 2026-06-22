from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX_PATH = ROOT / "data" / "literature" / "literature.sqlite3"


@dataclass(frozen=True)
class LiteratureHit:
    title: str
    collection: str
    text: str
    source: str
    url: str
    language: str


def _normalize_query(query: str) -> str:
    words = re.findall(r"[\w']+", query.lower(), flags=re.UNICODE)
    synonyms = {
        "шаг": ["шаг", "step"],
        "шаги": ["шаг", "step"],
        "первый": ["первый", "one"],
        "первого": ["первый", "one"],
        "бессилие": ["бессилие", "powerless"],
        "алкоголь": ["алкоголь", "alcohol"],
        "традиция": ["традиция", "tradition"],
        "спонсор": ["спонсор", "наставничество", "sponsor"],
        "наставник": ["наставник", "наставничество", "sponsor"],
        "новичок": ["новичок", "newcomer"],
    }
    expanded: list[str] = []
    for word in words:
        expanded.extend(synonyms.get(word, [word]))
    stop = {
        "а",
        "и",
        "или",
        "что",
        "как",
        "мне",
        "про",
        "это",
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "about",
        "me",
        "what",
        "how",
    }
    terms = [word for word in expanded if len(word) > 2 and word not in stop]
    return " OR ".join(terms[:8]) or query.strip()


def search_literature(query: str, limit: int = 3, index_path: Path = DEFAULT_INDEX_PATH) -> list[LiteratureHit]:
    if not query.strip() or not index_path.exists():
        return []
    fts_query = _normalize_query(query)
    try:
        with sqlite3.connect(index_path) as conn:
            rows = conn.execute(
                """
                SELECT title, collection, text, source, url, language
                FROM literature_fts
                WHERE literature_fts MATCH ?
                ORDER BY bm25(literature_fts)
                LIMIT ?
                """,
                (fts_query, limit),
            ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [LiteratureHit(title=row[0], collection=row[1], text=row[2], source=row[3], url=row[4], language=row[5]) for row in rows]


def format_literature_context(hits: list[LiteratureHit], max_chars: int = 1800) -> str:
    if not hits:
        return ""
    parts: list[str] = []
    used = 0
    for index, hit in enumerate(hits, start=1):
        excerpt = re.sub(r"\s+", " ", hit.text).strip()
        remaining = max_chars - used
        if remaining <= 0:
            break
        excerpt = excerpt[: max(0, remaining - 180)].strip()
        if not excerpt:
            break
        part = f"[{index}] {hit.collection}: {hit.title}\n{excerpt}\nИсточник: {hit.source}, {hit.url}"
        parts.append(part)
        used += len(part)
    return "\n\n".join(parts)


def literature_reply(query: str, lang: str = "ru") -> str:
    hits = search_literature(query, limit=3)
    if not hits:
        if lang != "ru":
            return "I don’t have a relevant literature passage yet. You can ask about a Step, Tradition, craving, meetings, or sponsorship."
        return "Пока не нашёл подходящий фрагмент в литературе. Можешь спросить про конкретный шаг, традицию, тягу, группу или спонсора."

    first = hits[0]
    excerpt = re.sub(r"\s+", " ", first.text).strip()[:700]
    if lang != "ru":
        return (
            f"I found this in A.A. literature:\n\n"
            f"*{first.collection}: {first.title}*\n"
            f"{excerpt}…\n\n"
            f"Source: {first.source}\n{first.url}"
        )
    return (
        f"Нашёл опору в литературе АА:\n\n"
        f"*{first.collection}: {first.title}*\n"
        f"{excerpt}…\n\n"
        f"Источник: {first.source}\n{first.url}"
    )
