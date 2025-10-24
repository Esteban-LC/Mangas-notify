# -*- coding: utf-8 -*-
import os
import requests
from typing import Optional, Dict, Any, Iterable

DISCORD_DEBUG = os.getenv("DISCORD_DEBUG", "0") == "1"

def _chunks(text: str, limit: int = 1900) -> Iterable[str]:
    text = text or ""
    while text:
        yield text[:limit]
        text = text[limit:]

def send_discord_message(webhook_url: str, content: str,
                         username: Optional[str] = None,
                         avatar_url: Optional[str] = None) -> bool:
    """
    Envía content fragmentado (Discord máx ~2000 chars). Devuelve True si TODOS los
    envíos devolvieron 2xx/204. Con DISCORD_DEBUG=1 imprime estado y body si falla.
    """
    if not webhook_url:
        if DISCORD_DEBUG:
            print("[discord] webhook vacío")
        return False

    ok = True
    headers = {"Content-Type": "application/json"}

    for part in _chunks(content, limit=1900):
        payload: Dict[str, Any] = {
            "content": part,
            "allowed_mentions": {"parse": []},  # evita @everyone etc.
        }
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url

        try:
            resp = requests.post(webhook_url, json=payload, headers=headers, timeout=20)
            if resp.status_code not in (200, 204):
                ok = False
                if DISCORD_DEBUG:
                    print(f"[discord] status={resp.status_code} body={resp.text[:400]}")
                # Si falla un chunk, paramos
                break
        except requests.RequestException as e:
            ok = False
            if DISCORD_DEBUG:
                print(f"[discord] error de red: {type(e).__name__}: {e}")
            break

    return ok
