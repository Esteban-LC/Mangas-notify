# -*- coding: utf-8 -*-
import os
import re
import yaml

def yprint(s: str) -> None:
    print(s, flush=True)

def load_yaml(path: str):
    if not os.path.exists(path):
        return {"series": []}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {"series": []}

def save_yaml(path: str, data):
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)

def comparable_tuple(s: str):
    if s is None:
        return (-1, -1)
    try:
        if "." in s:
            a, b = s.split(".", 1)
            return (int(a), int(b))
        return (int(s), 0)
    except:
        return (-1, -1)

def sanitize_chapter(s: str) -> str:
    s = s.strip()
    if "." in s:
        a, b = s.split(".", 1)
        a = str(int(a))
        b = b.rstrip("0")
        if b == "":
            return a
        return f"{a}.{b}"
    return str(int(s))

def sane_chapter_for_update(prev: str, new: str) -> bool:
    # Filter out absurd chapter ids like 771093 or 103116
    try:
        ent = new.split(".", 1)[0]
        if len(ent) > 4:
            return False
        if int(ent) > 1000:
            return False
        return True
    except:
        return False

def fmt_series_line(name: str, chap: str, status: str) -> str:
    emoji = {
        "update": "🟢",
        "init": "✨",
        "ok": "✅",
        "keep": "🛡️",
        "info": "ℹ️",
    }.get(status, "▪️")
    return f"{emoji} **{name}** — cap **{chap}** ({status})"
