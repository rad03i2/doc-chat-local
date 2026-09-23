from __future__ import annotations
import argparse
import sys
from pathlib import Path
from .core import DocumentIndex, SUPPORTED


def collect(inputs: list[str]) -> list[Path]:
    out: list[Path] = []
    for value in inputs:
        p = Path(value)
        if p.is_dir(): out.extend(sorted(x for x in p.rglob("*") if x.is_file() and x.suffix.lower() in SUPPORTED))
        elif p.is_file(): out.append(p)
        else: raise FileNotFoundError(value)
    seen = set(); unique = []
    for p in out:
        r = p.resolve()
        if r not in seen: seen.add(r); unique.append(p)
    return unique


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="doc-chat", description="Private local document search and extractive Q&A")
    p.add_argument("--version", action="version", version="doc-chat-local 1.0.0 — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Build a portable local index")
    b.add_argument("inputs", nargs="+"); b.add_argument("-o", "--output", default="doc-index.json")
    b.add_argument("--chunk-size", type=int, default=900); b.add_argument("--overlap", type=int, default=120)
    s = sub.add_parser("search", help="Search an existing index")
    s.add_argument("index"); s.add_argument("query"); s.add_argument("-n", "--limit", type=int, default=5)
    a = sub.add_parser("ask", help="Return cited relevant passages")
    a.add_argument("index"); a.add_argument("question"); a.add_argument("-n", "--limit", type=int, default=3)
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.cmd == "build":
            files = collect(args.inputs)
            if not files: raise ValueError("No supported documents found")
            idx = DocumentIndex.from_paths(files, args.chunk_size, args.overlap); idx.save(Path(args.output))
            print(f"Indexed {len(files)} document(s) into {len(idx.chunks)} chunk(s): {args.output}")
        elif args.cmd == "search":
            for i, h in enumerate(DocumentIndex.load(Path(args.index)).search(args.query, args.limit), 1):
                print(f"[{i}] score={h.score:.3f} {h.source}#chunk-{h.chunk}\n{h.text}\n")
        else: print(DocumentIndex.load(Path(args.index)).answer(args.question, args.limit))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
