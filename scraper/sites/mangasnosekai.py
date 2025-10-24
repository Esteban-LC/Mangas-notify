# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from typing import Optional, List
from ..utils import comparable_tuple, sanitize_chapter

CAP_RE  = re.compile(r"(?:Cap(?:[íi]tulo)?|Cap\.)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
CH_RE   = re.compile(r"Ch(?:apter|\.)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
EP_RE   = re.compile(r"(?:Episodio|Ep\.)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
HASH_RE = re.compile(r"#\s*(\d+(?:[.,]\d+)?)")

def _is_sane(num_str: str) -> bool:
    try:
        ent = num_str.split(".", 1)[0]
        if len(ent) > 4:
            return False
        if int(ent) > 1000:
            return False
        return True
    except Exception:
        return False

def parse_latest_chapter(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []
    for a in soup.select("a"):
        t = a.get_text(" ", strip=True)
        m = CAP_RE.search(t) or CH_RE.search(t) or EP_RE.search(t) or HASH_RE.search(t)
        if not m:
            # prueba también en el href
            href = a.get("href") or ""
            m = CAP_RE.search(href) or CH_RE.search(href) or EP_RE.search(href) or HASH_RE.search(href)
        if m:
            cap = sanitize_chapter(m.group(1))
            if _is_sane(cap):
                candidates.append(cap)

    if not candidates:
        # fallback: buscar en contenedores comunes de WP Manga
        for sel in (".chapter-list", ".wp-manga-chapter", "body"):
            cont = soup.select_one(sel)
            if not cont:
                continue
            text = cont.get_text(" ", strip=True)
            for m in (CAP_RE.finditer(text) or []):
                cap = sanitize_chapter(m.group(1))
                if _is_sane(cap):
                    candidates.append(cap)
            if candidates:
                break

    if not candidates:
        return None

    candidates.sort(key=lambda s: comparable_tuple(s))
    return candidates[-1]
