# -*- coding: utf-8 -*-
from typing import Optional
from playwright.sync_api import sync_playwright
import time

def fetch_html(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 30000) -> str:
    """
    Fetch robusto con:
      - user-agent "realista"
      - reintentos
      - --no-sandbox (para runners)
    """
    attempts = 3
    last_exc: Optional[Exception] = None

    with sync_playwright() as p:
        for i in range(attempts):
            browser = None
            context = None
            try:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context(user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ))
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                if wait_selector:
                    page.wait_for_selector(wait_selector, timeout=timeout_ms)
                html = page.content()
                return html
            except Exception as e:
                last_exc = e
                time.sleep(1 + i)  # backoff leve
            finally:
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

    # Si nunca retornó, eleva el último error
    if last_exc:
        raise last_exc
    raise RuntimeError("fetch_html falló sin excepción registrada")
