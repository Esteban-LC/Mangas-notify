# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from typing import Optional, List
from ..utils import comparable_tuple, sanitize_chapter

# Patrones de número: "# 12", "Cap. 12", "Ch. 12", "Chapter 12", admite coma
HASH_NUM = re.compile(r"#\s*(\d+(?:[.,]\d+)?)")
CAP_RE   = re.compile(r"(?:Cap(?:[íi]tulo)?|Cap\.|Ch(?:apter|\.)?)\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)

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

    # 1) Preferir anchors con trayectorias típicas
    for a in soup.select("a"):
        href = (a.get("href") or "").lower()
        if not href:
            continue
        # Heurística: URLs que suelen indicar capítulo
        looks_like_chapter = any(seg in href for seg in ("/chapter", "/cap", "/ep", "/episodio"))
        text = a.get_text(" ", strip=True)

        m = HASH_NUM.search(text) or CAP_RE.search(text)
        if not (m or looks_like_chapter):
            continue

        # si la URL luce a capítulo pero el texto no trae número, intenta en el href
        if not m:
            m = HASH_NUM.search(href) or CAP_RE.search(href)

        if not m:
            continue

        cap = sanitize_chapter(m.group(1))
        if _is_sane(cap):
            candidates.append(cap)

    # 2) Fallback: la antigua lista con clase ofuscada (por si sigue existiendo)
    if not candidates:
        for li in soup.select('li[class*="DTyuZxQygzByzNbtcmg-lis"]'):
            text = li.get_text(" ", strip=True)
            m = HASH_NUM.search(text) or CAP_RE.search(text)
            if not m:
                continue
            cap = sanitize_chapter(m.group(1))
            if _is_sane(cap):
                candidates.append(cap)

    if not candidates:
        return None

    candidates.sort(key=lambda s: comparable_tuple(s))
    return candidates[-1]
