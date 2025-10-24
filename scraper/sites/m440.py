# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from typing import Optional, List
from ..utils import comparable_tuple, sanitize_chapter

HASH_NUM = re.compile(r"#\s*(\d+(?:\.\d+)?)")

def parse_latest_chapter(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []

    for li in soup.select('li[class*="DTyuZxQygzByzNbtcmg-lis"]'):
        text = li.get_text(" ", strip=True)
        m = HASH_NUM.search(text)
        if not m:
            continue
        cap = sanitize_chapter(m.group(1))
        ent = cap.split(".", 1)[0]
        try:
            if len(ent) > 4 or int(ent) > 1000:
                continue
        except:
            continue
        candidates.append(cap)

    if not candidates:
        return None

    candidates.sort(key=lambda s: comparable_tuple(s))
    return candidates[-1]
