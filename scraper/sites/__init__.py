# -*- coding: utf-8 -*-
from typing import Callable
from .animebbg import parse_latest_chapter as parse_animebbg
from .m440 import parse_latest_chapter as parse_m440
from .bokugents import parse_latest_chapter as parse_bokugents
from .mangasnosekai import parse_latest_chapter as parse_msk
from .zonatmo import parse_latest_chapter as parse_zonatmo

def get_parser_for_url(url: str) -> Callable[[str], str]:
    u = url.lower()
    if "animebbg.net" in u:
        return parse_animebbg
    if "m440.in" in u:
        return parse_m440
    if "bokugents.com" in u:
        return parse_bokugents
    if "mangasnosekai.com" in u:
        return parse_msk
    if "zonatmo.com" in u:
        return parse_zonatmo
    return parse_bokugents
