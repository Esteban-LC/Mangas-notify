# -*- coding: utf-8 -*-
import json
import urllib.request

def send_discord_message(webhook_url: str, content: str) -> bool:
    data = {"content": content[:1800]}
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False
