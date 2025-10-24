# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from typing import Optional, List
from ..utils import comparable_tuple, sanitize_chapter

CAP_RE = re.compile(r"Cap[ií]tulo\s+(\d+(?:\.\d+)?)", re.IGNORECASE)

def _is_sane(num_str: str) -> bool:
    try:
        ent = num_str.split(".", 1)[0]
        if len(ent) > 4:
            return False
        if int(ent) > 1000:
            return False
        return True
    except:
        return False

def parse_latest_chapter(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []

    for a in soup.select('.structItem-cell--main .structItem-title a[href*="/comics/capitulo/"]'):
        m = CAP_RE.search(a.get_text(" ", strip=True))
        if m:
            cap = sanitize_chapter(m.group(1))
            if _is_sane(cap):
                candidates.append(cap)

    if not candidates:
        cont = soup.select_one('.block-container.structItem--resourceAlbum')
        if cont:
            text = cont.get_text(" ", strip=True)
            for m in CAP_RE.finditer(text):
                cap = sanitize_chapter(m.group(1))
                if _is_sane(cap):
                    candidates.append(cap)

    if not candidates:
        return None

    candidates.sort(key=lambda s: comparable_tuple(s))
    return candidates[-1]
