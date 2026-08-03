import argparse
import json
import re
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


def extract_docinfo(path: Path) -> dict:
    reader = PdfReader(str(path))
    meta = reader.metadata or {}

    def get_meta(key: str):
        v = meta.get(key)
        if v is None:
            return None
        return _clean(str(v))

    return {
        "pages": len(reader.pages),
        "title": get_meta("/Title"),
        "author": get_meta("/Author"),
        "subject": get_meta("/Subject"),
        "creator": get_meta("/Creator"),
        "producer": get_meta("/Producer"),
    }


FIG_RE = re.compile(r"^\s*(Figure|Fig\.?|Table)\s+\d+(\.|:)", re.IGNORECASE)


def extract_text_sample(path: Path, max_pages: int) -> str:
    out = []
    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages[:max_pages]):
            txt = page.extract_text() or ""
            txt = txt.replace("\u00ad", "")
            out.append(txt)
    return "\n".join(out)


def extract_caption_lines(text: str, max_items: int) -> list[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    hits: list[str] = []
    for l in lines:
        if FIG_RE.search(l):
            hits.append(_clean(l))
        if len(hits) >= max_items:
            break
    return hits


def keyword_snippets(text: str, keywords: list[str], max_hits_per_kw: int) -> dict[str, list[str]]:
    # Build simple context snippets around each keyword.
    results: dict[str, list[str]] = {k: [] for k in keywords}
    if not text:
        return results

    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        for m in pattern.finditer(text):
            start = max(0, m.start() - 140)
            end = min(len(text), m.end() + 160)
            snippet = _clean(text[start:end])
            if snippet and snippet not in results[kw]:
                results[kw].append(snippet)
            if len(results[kw]) >= max_hits_per_kw:
                break
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=str, help="Path to PDF")
    ap.add_argument("--max-pages", type=int, default=8)
    ap.add_argument("--max-captions", type=int, default=60)
    ap.add_argument("--max-hits", type=int, default=6)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--captions-only", action="store_true", help="Print only figure/table caption lines")
    ap.add_argument("--first-page", action="store_true", help="Print extracted text from first page")
    ap.add_argument("--grep", action="append", default=[], help="Regex/text to search in full extracted text; can be repeated")
    ap.add_argument("--grep-context", type=int, default=220, help="Characters of context around each grep match")
    args = ap.parse_args()

    path = Path(args.pdf)
    if not path.exists():
        raise SystemExit(f"PDF not found: {path}")

    info = extract_docinfo(path)

    if args.grep:
        reader = PdfReader(str(path))
        full = "\n".join((pg.extract_text() or "") for pg in reader.pages)
        for pat in args.grep:
            try:
                rx = re.compile(pat, re.IGNORECASE)
            except re.error:
                rx = re.compile(re.escape(pat), re.IGNORECASE)
            m = rx.search(full)
            if not m:
                print(f"[MISS] {pat}")
                continue
            start = max(0, m.start() - args.grep_context)
            end = min(len(full), m.end() + args.grep_context)
            snippet = _clean(full[start:end])
            print(f"[HIT] {pat}: {snippet}")
        return 0

    if args.first_page:
        reader = PdfReader(str(path))
        first = reader.pages[0].extract_text() or ""
        print(first)
        return 0

    text = extract_text_sample(path, max_pages=args.max_pages)
    captions = extract_caption_lines(text, max_items=args.max_captions)

    if args.captions_only:
        seen: set[str] = set()
        for c in captions:
            if c in seen:
                continue
            seen.add(c)
            print(c)
        return 0

    keywords = [
        "experimental", "setup", "testbed", "measurement", "measured", "instrument",
        "PDU", "power analyzer", "sampling", "averaging", "window", "synchronize",
        "RU", "O-RU", "O-DU", "O-CU", "Amarisoft", "UE", "traffic",
        "PRB", "throughput", "Grafana", "Prometheus", "Kepler", "Scaphandre",
        "IPMI", "Redfish", "kubernetes", "bare metal",
    ]
    snippets = keyword_snippets(text, keywords=keywords, max_hits_per_kw=args.max_hits)

    result = {
        "file": str(path.as_posix()),
        "docinfo": info,
        "captions_sample": captions,
        "keyword_snippets": {k: v for k, v in snippets.items() if v},
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"FILE: {result['file']}")
        print(f"PAGES: {info['pages']}")
        for k in ["title", "author", "subject", "creator", "producer"]:
            if info.get(k):
                print(f"{k.upper()}: {info[k]}")
        print("\nCAPTIONS (sample):")
        for c in captions[: min(25, len(captions))]:
            print(f"- {c}")
        print("\nKEYWORD HITS (sample):")
        for k, vals in result["keyword_snippets"].items():
            print(f"\n[{k}]")
            for v in vals[: min(3, len(vals))]:
                print(f"- {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
