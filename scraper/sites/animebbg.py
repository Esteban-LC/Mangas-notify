# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from typing import Optional, List
from ..utils import comparable_tuple, sanitize_chapter

# Acepta Capítulo/Cap./Chapter/Ch./Episodio/Ep. y coma decimal
CAP_RE = re.compile(
    r"(?:Cap(?:[íi]tulo)?|Cap\.|Ch(?:apter|\.)|Episodio|Ep\.)\s*(\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)
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

    # 1) Enlaces
    for a in soup.select("a"):
        text = a.get_text(" ", strip=True)
        m = CAP_RE.search(text) or HASH_RE.search(text) or CAP_RE.search((a.get("href") or ""))
        if not m:
            continue
        cap = sanitize_chapter(m.group(1))
        if _is_sane(cap):
            candidates.append(cap)

    # 2) Fallback: contenedores comunes
    if not candidates:
        for sel in (".block-container", ".structItemContainer", "body"):
            cont = soup.select_one(sel)
            if not cont:
                continue
            text = cont.get_text(" ", strip=True)
            for m in CAP_RE.finditer(text):
                cap = sanitize_chapter(m.group(1))
                if _is_sane(cap):
                    candidates.append(cap)
            if candidates:
                break

    if not candidates:
        return None

    candidates.sort(key=lambda s: comparable_tuple(s))
    return candidates[-1]
