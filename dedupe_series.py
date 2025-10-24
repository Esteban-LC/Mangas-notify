# -*- coding: utf-8 -*-
"""
Deduplica series por URL, conservando la entrada con capítulo más alto.
Normaliza URL mínimamente:
  - quita espacios
  - lower-case en esquema/host
  - quita slash final (salvo raíz)
Uso:
  python dedupe_series.py
"""
import yaml
from collections import OrderedDict
from urllib.parse import urlparse, urlunparse

SERIES_FILE = "series.yaml"

def normalize_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return u
    p = urlparse(u)
    scheme = (p.scheme or "").lower()
    netloc = (p.netloc or "").lower()
    path = p.path or ""
    # quita slash final si no es raíz
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]
    newp = p._replace(scheme=scheme, netloc=netloc, path=path)
    return urlunparse(newp)

def comparable_tuple(ch: str):
    """Pequeña copia local, por si alguien ejecuta esto fuera del paquete."""
    ch = str(ch or "0")
    parts = ch.replace(",", ".").split(".")
    major = int(parts[0]) if parts[0].isdigit() else 0
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (major, minor)

def load_yaml(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {"series": []}
    except FileNotFoundError:
        return {"series": []}

def save_yaml(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def main():
    data = load_yaml(SERIES_FILE)
    series = data.get("series", [])
    best: "OrderedDict[str, dict]" = OrderedDict()

    for e in series:
        u = normalize_url(e.get("url", ""))
        if not u:
            continue
        cur = str(e.get("chapter") or "0")
        if u not in best:
            best[u] = e
        else:
            prev = str(best[u].get("chapter") or "0")
            best[u] = e if (comparable_tuple(cur) > comparable_tuple(prev)) else best[u]

    out = {"series": list(best.values())}
    save_yaml(SERIES_FILE, out)
    print(f"Quedaron {len(out['series'])} series únicas.")

if __name__ == "__main__":
    main()
