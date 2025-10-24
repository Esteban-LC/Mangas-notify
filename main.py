# -*- coding: utf-8 -*-
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

from scraper.utils import (
    load_yaml, save_yaml, yprint, comparable_tuple, sanitize_chapter,
    sane_chapter_for_update, fmt_series_line
)
from scraper.fetchers import fetch_html
from scraper.discord import send_discord_message
from scraper.sites import get_parser_for_url, get_wait_selector_for_url

SERIES_FILE = "series.yaml"

def _url_looks_bad(u: str) -> Optional[str]:
    if not (u.startswith("http://") or u.startswith("https://")):
        return "sin esquema (http/https)"
    if "..." in u:
        return "URL truncada (contiene '...')"
    parsed = urlparse(u)
    if not parsed.netloc or not parsed.path:
        return "host o path vacío"
    return None

def process_series_entry(entry: Dict[str, Any]) -> Tuple[str, str, Optional[str], Optional[str], str]:
    """
    Return (name, url, prev_chapter, current_chapter, status)
    status: 'init' | 'update' | 'ok' | 'keep' | 'info'
    """
    name = entry["name"].strip()
    url  = entry["url"].strip()
    prev = str(entry.get("chapter") or "").strip() or None

    bad = _url_looks_bad(url)
    if bad:
        yprint(f"   [info] URL inválida: {bad}")
        return name, url, prev, prev or "0", "info"

    parser = get_parser_for_url(url)
    wait_selector = get_wait_selector_for_url(url)

    html = fetch_html(url, wait_selector=wait_selector, timeout_ms=30000)
    cur  = parser(html)

    if cur is None:
        return name, url, prev, prev or "0", "info"

    if prev is None:
        return name, url, None, cur, "init"

    if not sane_chapter_for_update(prev, cur):
        # No bajamos capítulo si cur < prev
        return name, url, prev, prev, "keep"

    if comparable_tuple(cur) > comparable_tuple(prev):
        return name, url, prev, cur, "update"

    return name, url, prev, prev, "ok"

def main() -> int:
    cfg = {
        "FETCH_BACKEND": os.getenv("FETCH_BACKEND", "playwright"),
        "HTTPS_PROXY": os.getenv("HTTPS_PROXY", "unset"),
        "HTTP_PROXY": os.getenv("HTTP_PROXY", "unset"),
    }
    yprint(f"[cfg] FETCH_BACKEND='{cfg['FETCH_BACKEND']}'  HTTPS_PROXY={cfg['HTTPS_PROXY']}  HTTP_PROXY={cfg['HTTP_PROXY']}")

    data = load_yaml(SERIES_FILE)
    series: List[Dict[str, Any]] = data.get("series", [])

    results = []
    changed = False

    for s in series:
        yprint(f"==> {s['name']}")
        try:
            name, url, prev, cur, status = process_series_entry(s)
        except Exception as e:
            yprint(f"   [skip] error: {e}")
            continue

        if status == "init":
            yprint(f"   [init] last_chapter = {cur}")
            s["chapter"] = cur
            changed = True
        elif status == "update":
            yprint(f"   [update] {prev} → {cur}")
            s["chapter"] = cur
            changed = True
        elif status == "ok":
            yprint(f"   [ok] sin cambios (cap {cur})")
        elif status == "keep":
            yprint(f"   [keep] {prev} (ignorado {cur})")
        else:
            yprint("   [info] no se detectó capítulo válido")

        results.append({"name": name, "cur": cur, "status": status})

    updates = [r for r in results if r["status"] == "update"]
    inits   = [r for r in results if r["status"] == "init"]
    oks     = [r for r in results if r["status"] == "ok"]
    keeps   = [r for r in results if r["status"] == "keep"]
    infos   = [r for r in results if r["status"] == "info"]

    yprint("\nResumen:")
    yprint(f"  Actualizados: {len(updates)}")
    yprint(f"  Nuevos (init): {len(inits)}")
    yprint(f"  Sin actualización: {len(oks)}")
    yprint(f"  Mantenidos (keep): {len(keeps)}")
    yprint(f"  Info: {len(infos)}")

    # Mensaje unificado para Discord
    lines = []
    for r in results:
        pretty = fmt_series_line(r["name"], r["cur"], r["status"])
        lines.append(pretty)
    body = "**Estado de tus series**\n" + "\n".join(lines)

    webhook = os.getenv("DISCORD_WEBHOOK")
    if webhook:
        ok = send_discord_message(webhook, body)
        if not ok:
            yprint("[warn] Discord no respondió OK (silenciado).")
    else:
        yprint("[info] DISCORD_WEBHOOK no definido; no se envía a Discord.")

    # Commit opcional
    if changed and os.getenv("CI"):
        os.system('git config user.name "github-actions[bot]"')
        os.system('git config user.email "github-actions[bot]@users.noreply.github.com"')
        os.system("git add series.yaml")
        os.system('git commit -m "chore: update last_chapter [skip ci]" || true')
        push_res = os.system("git push || true")
        if push_res != 0:
            yprint("[warn] git push no autorizado o falló; continuando sin fallar el job.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
