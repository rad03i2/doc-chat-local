from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[\w\u0600-\u06ff]+", re.UNICODE)
SUPPORTED = {".txt", ".md", ".pdf"}

@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str

@dataclass(frozen=True)
class Hit:
    source: str
    chunk: int
    score: float
    text: str


def tokenize(text: str) -> list[str]:
    return [x.casefold() for x in TOKEN_RE.findall(text) if len(x) > 1]


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {suffix or '<none>'}")
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, source: str, size: int = 900, overlap: int = 120) -> list[Chunk]:
    if size < 100 or overlap < 0 or overlap >= size:
        raise ValueError("size must be >=100 and 0 <= overlap < size")
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return []
    out, start, idx = [], 0, 0
    while start < len(clean):
        end = min(len(clean), start + size)
        if end < len(clean):
            boundary = clean.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        piece = clean[start:end].strip()
        if piece:
            out.append(Chunk(source, idx, piece)); idx += 1
        if end >= len(clean): break
        start = max(start + 1, end - overlap)
    return out


class DocumentIndex:
    """Small, deterministic, fully local TF-IDF document index."""
    def __init__(self, chunks: Iterable[Chunk]):
        self.chunks = list(chunks)
        self._tokens = [Counter(tokenize(c.text)) for c in self.chunks]
        df = Counter()
        for counts in self._tokens:
            df.update(counts.keys())
        n = max(1, len(self.chunks))
        self._idf = {t: math.log((n + 1) / (freq + 1)) + 1 for t, freq in df.items()}

    @classmethod
    def from_paths(cls, paths: Iterable[Path], size: int = 900, overlap: int = 120) -> "DocumentIndex":
        chunks: list[Chunk] = []
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(path)
            chunks.extend(chunk_text(read_document(path), str(path), size, overlap))
        return cls(chunks)

    def search(self, query: str, limit: int = 5) -> list[Hit]:
        q = Counter(tokenize(query))
        if not q or limit < 1: return []
        qv = {t: c * self._idf.get(t, 1.0) for t, c in q.items()}
        qnorm = math.sqrt(sum(v*v for v in qv.values())) or 1
        hits = []
        for chunk, counts in zip(self.chunks, self._tokens):
            dv = {t: c * self._idf.get(t, 1.0) for t, c in counts.items()}
            dnorm = math.sqrt(sum(v*v for v in dv.values())) or 1
            dot = sum(qv.get(t, 0) * v for t, v in dv.items())
            score = dot / (qnorm * dnorm)
            if score > 0: hits.append(Hit(chunk.source, chunk.index, score, chunk.text))
        return sorted(hits, key=lambda h: (-h.score, h.source, h.chunk))[:limit]

    def answer(self, question: str, limit: int = 3) -> str:
        hits = self.search(question, limit)
        if not hits:
            return "No relevant passage was found in the indexed documents."
        parts = ["Most relevant passages (extractive answer):"]
        for i, h in enumerate(hits, 1):
            parts.append(f"\n[{i}] {h.text}\nSource: {h.source}#chunk-{h.chunk} (score {h.score:.3f})")
        return "\n".join(parts)

    def save(self, path: Path) -> None:
        path.write_text(json.dumps([asdict(c) for c in self.chunks], ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "DocumentIndex":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list): raise ValueError("Invalid index format")
        return cls(Chunk(str(x["source"]), int(x["index"]), str(x["text"])) for x in raw)
