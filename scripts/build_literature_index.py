from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SOURCES = [
    (ROOT / "knowledge_manifest.json", ROOT / "data" / "literature" / "raw_pdfs"),
    (ROOT / "knowledge_manifest_ru.json", ROOT / "data" / "literature" / "raw_pdfs_ru"),
]
TEXT_DIR = ROOT / "data" / "literature" / "texts"
INDEX_PATH = ROOT / "data" / "literature" / "literature.sqlite3"


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    pages: list[str] = []
    for page in doc:
        pages.append(page.get_text("text"))
    return normalize_text("\n\n".join(pages))


def chunk_text(text: str, max_chars: int = 1400, overlap: int = 220) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current.strip():
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(paragraph):
                part = paragraph[start : start + max_chars].strip()
                if part:
                    chunks.append(part)
                start += max_chars - overlap
            continue
        if len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}" if current else paragraph
        else:
            if current.strip():
                chunks.append(current.strip())
            tail = current[-overlap:] if current else ""
            current = f"{tail}\n\n{paragraph}" if tail else paragraph
    if current.strip():
        chunks.append(current.strip())
    return chunks


def build() -> dict[str, int]:
    sources: list[tuple[dict, Path]] = []
    for manifest_path, pdf_dir in MANIFEST_SOURCES:
        if not manifest_path.exists():
            continue
        for item in json.loads(manifest_path.read_text(encoding="utf-8")):
            sources.append((item, pdf_dir))
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(INDEX_PATH)
    conn.execute("DROP TABLE IF EXISTS literature_chunks")
    conn.execute("DROP TABLE IF EXISTS literature_documents")
    conn.execute("DROP TABLE IF EXISTS literature_fts")
    conn.execute(
        """
        CREATE TABLE literature_documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            collection TEXT NOT NULL,
            language TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            text_path TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE literature_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            title TEXT NOT NULL,
            collection TEXT NOT NULL,
            language TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            text TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE literature_fts USING fts5(
            text,
            title,
            collection,
            language UNINDEXED,
            source UNINDEXED,
            url UNINDEXED,
            document_id UNINDEXED,
            chunk_id UNINDEXED,
            tokenize='unicode61 remove_diacritics 2'
        )
        """
    )

    docs = 0
    chunks_total = 0
    for item, pdf_dir in sources:
        pdf_path = pdf_dir / f"{item['id']}.pdf"
        text = extract_pdf_text(pdf_path)
        text_path = TEXT_DIR / f"{item['id']}.txt"
        text_path.write_text(text, encoding="utf-8")
        conn.execute(
            "INSERT INTO literature_documents VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                item["id"],
                item["title"],
                item["collection"],
                item["language"],
                item["source"],
                item["url"],
                str(text_path.relative_to(ROOT)),
            ),
        )
        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            cur = conn.execute(
                """
                INSERT INTO literature_chunks
                (document_id, chunk_index, title, collection, language, source, url, text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    idx,
                    item["title"],
                    item["collection"],
                    item["language"],
                    item["source"],
                    item["url"],
                    chunk,
                ),
            )
            chunk_id = cur.lastrowid
            conn.execute(
                "INSERT INTO literature_fts (text, title, collection, language, source, url, document_id, chunk_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (chunk, item["title"], item["collection"], item["language"], item["source"], item["url"], item["id"], chunk_id),
            )
        docs += 1
        chunks_total += len(chunks)

    conn.commit()
    conn.close()
    return {"documents": docs, "chunks": chunks_total}


if __name__ == "__main__":
    stats = build()
    print(json.dumps(stats, ensure_ascii=False))
