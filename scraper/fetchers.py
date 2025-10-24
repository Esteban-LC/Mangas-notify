# -*- coding: utf-8 -*-
from typing import Optional
from playwright.sync_api import sync_playwright

def fetch_html(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 20000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        if wait_selector:
            page.wait_for_selector(wait_selector, timeout=timeout_ms)
        html = page.content()
        context.close()
        browser.close()
        return html
