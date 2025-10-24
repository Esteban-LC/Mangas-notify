# -*- coding: utf-8 -*-
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright
import time
import os
import re

DUMPS_DIR = os.getenv("HTML_DUMPS_DIR", "last_html")
os.makedirs(DUMPS_DIR, exist_ok=True)

ANTI_BOT_PATTERNS = [
    # Inglés
    r"Just a moment",
    r"Checking your browser before accessing",
    r"Attention Required!\s*\|\s*Cloudflare",
    r"cf-error-details",
    r"cf-please-wait",
    r"__cf_chl_captcha",
    r"hcaptcha",
    r"Please enable JavaScript and Cookies",
    # Español (¡clave para tus logs!)
    r"Un momento",
    r"Comprobando tu navegador antes de acceder",
    r"Atenci[oó]n requerida",
    r"Por favor (habilita|activa) JavaScript y las Cookies",
]

def _looks_like_antibot(html: str) -> bool:
    if not html:
        return True
    txt = html[:120000]
    for pat in ANTI_BOT_PATTERNS:
        if re.search(pat, txt, re.IGNORECASE):
            return True
    return False

def _safe_close(context, browser):
    try:
        if context:
            context.close()
    except Exception:
        pass
    try:
        if browser:
            browser.close()
    except Exception:
        pass

def _dump_html(kind: str, name: str, html: str) -> str:
    slug = re.sub(r"[^a-z0-9\-_.]+", "_", name.lower())[:80]
    path = os.path.join(DUMPS_DIR, f"{slug}.{kind}.html")
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html or "")
    except Exception:
        pass
    return path

def _try_fetch(p, browser_name: str, url: str, wait_selector: Optional[str], timeout_ms: int) -> Tuple[str, str]:
    ua_map = {
        "chromium": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "firefox":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "webkit":   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    }
    browser = context = page = None
    try:
        engine = getattr(p, browser_name)
        browser = engine.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            user_agent=ua_map.get(browser_name, ua_map["chromium"]),
            locale="es-MX",
            timezone_id="America/Mexico_City",
            viewport={"width": 1366, "height": 850},
            java_script_enabled=True,
        )
        context.set_extra_http_headers({
            "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/",
        })
        page = context.new_page()

        # Primer modo
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
            except Exception:
                pass
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.0)
        html = page.content()
        title = page.title()

        # Segundo intento si parece anti-bot
        if _looks_like_antibot(html):
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=timeout_ms)
                except Exception:
                    pass
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.2)
            html = page.content()
            title = page.title()

        return html, title
    finally:
        _safe_close(context, browser)

def fetch_html(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 30000,
               series_name: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    """
    Devuelve (html, title, antibot_reason)
    - Intenta Chromium, Firefox y WebKit
    - Marca como antibot si detecta challenge; vuelca HTML en last_html/
    """
    with sync_playwright() as p:
        reasons = []

        for engine in ("chromium", "firefox", "webkit"):
            try:
                html, title = _try_fetch(p, engine, url, wait_selector, timeout_ms)
                if not _looks_like_antibot(html):
                    return html, title, None
                reasons.append(f"{engine}/antibot")
                _dump_html(engine, series_name or "unknown", html)
            except Exception as e:
                reasons.append(f"{engine}/{type(e).__name__}")
            time.sleep(0.6)

    return html if 'html' in locals() else "", title if 'title' in locals() else "", "; ".join(reasons) or "blocked"
