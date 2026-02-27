"""Resolve DuckDB country strings to ISO3 codes and lat/lon centroids.

Usage:
    from dashboard_api.geo import resolve_country

    info = resolve_country("USA")
    # -> {"iso3": "USA", "name": "United States", "lat": 37.09, "lon": -95.71}
    # or None if unresolved.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_ASSETS_DIR = Path(__file__).parent / "assets"

# ── centroid map: iso3 -> {iso3, name, lat, lon} ─────────────────────────────
_CENTROID_MAP: dict[str, dict[str, Any]] = {}

# ── reverse name map: lowered name -> iso3 ───────────────────────────────────
_NAME_TO_ISO3: dict[str, str] = {}


def _load_centroids() -> None:
    """Load the centroid file once."""
    global _CENTROID_MAP, _NAME_TO_ISO3
    if _CENTROID_MAP:
        return
    path = _ASSETS_DIR / "country_centroids.json"
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)
    for entry in entries:
        iso3 = entry["iso3"]
        _CENTROID_MAP[iso3] = entry
        _NAME_TO_ISO3[entry["name"].lower()] = iso3


# ── common aliases that pycountry might not handle or that differ from the
#    centroid file's canonical names ───────────────────────────────────────────
_ALIASES: dict[str, str] = {
    "usa": "USA",
    "united states": "USA",
    "united states of america": "USA",
    "uk": "GBR",
    "united kingdom": "GBR",
    "great britain": "GBR",
    "russia": "RUS",
    "russian federation": "RUS",
    "south korea": "KOR",
    "republic of korea": "KOR",
    "korea, republic of": "KOR",
    "north korea": "PRK",
    "korea, democratic people's republic of": "PRK",
    "china": "CHN",
    "people's republic of china": "CHN",
    "taiwan": "TWN",
    "iran": "IRN",
    "iran, islamic republic of": "IRN",
    "syria": "SYR",
    "syrian arab republic": "SYR",
    "tanzania": "TZA",
    "tanzania, united republic of": "TZA",
    "venezuela": "VEN",
    "venezuela, bolivarian republic of": "VEN",
    "bolivia": "BOL",
    "bolivia, plurinational state of": "BOL",
    "vietnam": "VNM",
    "viet nam": "VNM",
    "laos": "LAO",
    "lao people's democratic republic": "LAO",
    "ivory coast": "CIV",
    "côte d'ivoire": "CIV",
    "cote d'ivoire": "CIV",
    "czech republic": "CZE",
    "czechia": "CZE",
    "turkey": "TUR",
    "türkiye": "TUR",
    "saudi arabia": "SAU",
    "south africa": "ZAF",
    "democratic republic of the congo": "COD",
    "dr congo": "COD",
    "congo, democratic republic of the": "COD",
    "republic of the congo": "COG",
    "congo": "COG",
    "eswatini": "SWZ",
    "swaziland": "SWZ",
    "myanmar": "MMR",
    "burma": "MMR",
    "brunei": "BRN",
    "brunei darussalam": "BRN",
    "timor-leste": "TLS",
    "east timor": "TLS",
    "north macedonia": "MKD",
    "macedonia": "MKD",
    "cape verde": "CPV",
    "cabo verde": "CPV",
}

# ── optional pycountry fallback ──────────────────────────────────────────────
_pycountry = None
try:
    import pycountry as _pycountry  # type: ignore[no-redef]
except ImportError:
    pass


def _lookup_pycountry(name: str) -> str | None:
    """Try pycountry fuzzy lookup; return ISO3 or None."""
    if _pycountry is None:
        return None
    try:
        match = _pycountry.countries.lookup(name)
        return match.alpha_3  # type: ignore[union-attr]
    except LookupError:
        return None


# ── public API ───────────────────────────────────────────────────────────────

_resolve_stats: dict[str, int] = {"resolved": 0, "unresolved": 0}


def resolve_country(country: str) -> dict[str, Any] | None:
    """Resolve a DuckDB country string to {iso3, name, lat, lon} or None.

    Resolution order:
    1. If the string is already an ISO3 code in the centroid map, use it.
    2. Check the alias dictionary (case-insensitive).
    3. Look up by centroid-file name (case-insensitive).
    4. Try pycountry.countries.lookup() if available.
    5. Return None (unresolved).
    """
    _load_centroids()

    # 1. Direct ISO3 match
    upper = country.strip().upper()
    if upper in _CENTROID_MAP:
        _resolve_stats["resolved"] += 1
        return _CENTROID_MAP[upper]

    # 2. Alias map
    lower = country.strip().lower()
    iso3 = _ALIASES.get(lower)
    if iso3 and iso3 in _CENTROID_MAP:
        _resolve_stats["resolved"] += 1
        return _CENTROID_MAP[iso3]

    # 3. Centroid-file name match
    iso3 = _NAME_TO_ISO3.get(lower)
    if iso3 and iso3 in _CENTROID_MAP:
        _resolve_stats["resolved"] += 1
        return _CENTROID_MAP[iso3]

    # 4. pycountry fallback
    iso3 = _lookup_pycountry(country.strip())
    if iso3 and iso3 in _CENTROID_MAP:
        _resolve_stats["resolved"] += 1
        return _CENTROID_MAP[iso3]

    _resolve_stats["unresolved"] += 1
    logger.warning("Could not resolve country to ISO3: %s", country)
    return None


def get_resolve_stats() -> dict[str, int]:
    """Return cumulative resolve hit/miss counts (useful for logging)."""
    return dict(_resolve_stats)
