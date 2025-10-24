# -*- coding: utf-8 -*-
from typing import Optional
from playwright.sync_api import sync_playwright
import time

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

def fetch_html(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 30000) -> str:
    """
    Fetch robusto:
      - user-agent realista
      - intenta 2 estrategias: domcontentloaded y networkidle
      - reintentos con pequeño backoff
      - scroll al fondo para lazy loads
      - --no-sandbox (GH Actions)
    """
    attempts = 3
    last_exc: Optional[Exception] = None

    with sync_playwright() as p:
        for i in range(attempts):
            browser = context = page = None
            try:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context(user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ))
                page = context.new_page()

                # 1) Primer intento: domcontentloaded
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                if wait_selector:
                    try:
                        page.wait_for_selector(wait_selector, timeout=timeout_ms)
                    except Exception:
                        pass
                # Scroll suave para disparar cargas diferidas
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.8)
                html = page.content()
                _safe_close(context, browser)
                return html
            except Exception as e1:
                last_exc = e1
                _safe_close(context, browser)
                time.sleep(0.8 + i)

            # 2) Segundo intento: networkidle
            try:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context(user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ))
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                if wait_selector:
                    try:
                        page.wait_for_selector(wait_selector, timeout=timeout_ms)
                    except Exception:
                        pass
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.8)
                html = page.content()
                _safe_close(context, browser)
                return html
            except Exception as e2:
                last_exc = e2
                _safe_close(context, browser)
                time.sleep(1.2 + i)

    if last_exc:
        raise last_exc
    raise RuntimeError("fetch_html falló sin excepción registrada")
