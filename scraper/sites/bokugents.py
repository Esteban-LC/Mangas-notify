# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from typing import Optional, List
from ..utils import comparable_tuple, sanitize_chapter

CAP_RE  = re.compile(r"(?:Cap(?:[íi]tulo)?|Cap\.)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
CH_RE   = re.compile(r"Ch(?:apter|\.)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
EP_RE   = re.compile(r"(?:Episodio|Ep\.)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
HASH_RE = re.compile(r"#\s*(\d+(?:[.,]\d+)?)")
ANYNUM  = re.compile(r"\b(\d{1,4}(?:[.,]\d{1,2})?)\b")

def _ok(n: str) -> bool:
    try:
        major = int(n.split(".", 1)[0])
        return 0 < major <= 1000
    except Exception:
        return False

def parse_latest_chapter(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    cands: List[str] = []

    # 1) anchors con patrones explícitos
    for a in soup.select("a"):
        t = a.get_text(" ", strip=True)
        m = CAP_RE.search(t) or CH_RE.search(t) or EP_RE.search(t) or HASH_RE.search(t)
        if not m:
            href = a.get("href") or ""
            m = CAP_RE.search(href) or CH_RE.search(href) or EP_RE.search(href) or HASH_RE.search(href)
        if m:
            ch = sanitize_chapter(m.group(1))
            if _ok(ch):
                cands.append(ch)

    # 2) fallback fuerte: si hay listas largas tipo índice, toma el MAYOR número cerca del texto de capítulo
    if not cands:
        for a in soup.select("a"):
            t = a.get_text(" ", strip=True)
            if re.search(r"(chapter|cap[ií]tulo|episodio|ep\.)", t, re.I):
                for m in ANYNUM.finditer(t):
                    ch = sanitize_chapter(m.group(1))
                    if _ok(ch):
                        cands.append(ch)

    if not cands:
        return None

    cands.sort(key=lambda s: comparable_tuple(s))
    return cands[-1]
