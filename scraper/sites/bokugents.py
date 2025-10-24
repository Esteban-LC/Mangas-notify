# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from typing import Optional, List
from ..utils import comparable_tuple, sanitize_chapter

CAP_RE = re.compile(r"Cap(?:[íi]tulo)?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)

def parse_latest_chapter(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []

    for a in soup.select('a'):
        t = a.get_text(" ", strip=True)
        m = CAP_RE.search(t) or re.search(r"#\s*(\d+(?:\.\d+)?)", t)
        if m:
            cap = sanitize_chapter(m.group(1))
            if len(cap.split(".",1)[0]) <= 4:
                candidates.append(cap)

    if not candidates:
        return None
    candidates.sort(key=lambda s: comparable_tuple(s))
    return candidates[-1]
