# -*- coding: utf-8 -*-
"""
Valida/depura series.yaml:
 - Deduplica por URL (normalizada) conservando capítulo mayor
 - Marca URLs truncadas (contienen '...')
 - Normaliza esquema/host (quita www), borra query/fragment y slash final
Uso:
  python validate_series.py
"""
import yaml
from urllib.parse import urlparse, urlunparse
from collections import OrderedDict

SERIES_FILE = "series.yaml"

def norm_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return u
    p = urlparse(u)
    scheme = (p.scheme or "https").lower()
    netloc = (p.netloc or "").lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = p.path or "/"
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]
    # quita query/fragment
    p2 = p._replace(scheme=scheme, netloc=netloc, path=path, query="", fragment="")
    return urlunparse(p2)

def chap_tuple(ch: str):
    ch = str(ch or "0").replace(",", ".")
    parts = ch.split(".")
    major = int(parts[0]) if parts and parts[0].isdigit() else 0
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (major, minor)

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {"series": []}

def save_yaml(path: str, data):
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)

def main():
    data = load_yaml(SERIES_FILE)
    series = data.get("series", [])

    bad_urls = []
    by_url = OrderedDict()

    for e in series:
        url = (e.get("url") or "").strip()
        if "..." in url or not (url.startswith("http://") or url.startswith("https://")):
            bad_urls.append((e.get("name", ""), url))
            # no lo metemos a dedupe; requiere corrección manual
            continue

        key = norm_url(url)
        prev = by_url.get(key)
        if not prev:
            by_url[key] = e
        else:
            # conserva capítulo mayor
            cur_ch = str(e.get("chapter") or "0")
            prev_ch = str(prev.get("chapter") or "0")
            by_url[key] = e if chap_tuple(cur_ch) > chap_tuple(prev_ch) else prev

    out = {"series": list(by_url.values())}
    save_yaml(SERIES_FILE, out)

    print(f"[ok] Deduplicado: quedaron {len(out['series'])} entradas.")
    if bad_urls:
        print("\n[warn] URLs inválidas/truncadas (corrige copiando la URL completa del navegador):")
        for name, url in bad_urls:
            print(f"  - {name}: {url}")

if __name__ == "__main__":
    main()
