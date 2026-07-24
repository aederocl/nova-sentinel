from __future__ import annotations

import math

# IAU 1958 Galactic pole and node, J2000 realization.
_RA_NGP = math.radians(192.85948)
_DEC_NGP = math.radians(27.12825)
_L_OMEGA = math.radians(32.93192)


def galactic_latitude(ra_deg: float, dec_deg: float) -> float:
    ra = math.radians(ra_deg)
    dec = math.radians(dec_deg)
    sin_b = (
        math.sin(dec) * math.sin(_DEC_NGP)
        + math.cos(dec) * math.cos(_DEC_NGP) * math.cos(ra - _RA_NGP)
    )
    return math.degrees(math.asin(max(-1.0, min(1.0, sin_b))))


def parse_sexagesimal(value: str, is_ra: bool) -> float | None:
    try:
        cleaned = value.strip().lower().replace("h", ":").replace("m", ":").replace("s", "")
        cleaned = cleaned.replace("d", ":").replace("°", ":").replace("'", ":").replace('"', "")
        parts = [float(x) for x in cleaned.replace(" ", ":").split(":") if x]
        if not parts:
            return None
        sign = -1 if parts[0] < 0 or value.strip().startswith("-") else 1
        total = abs(parts[0]) + (parts[1] / 60 if len(parts) > 1 else 0) + (parts[2] / 3600 if len(parts) > 2 else 0)
        return total * (15 if is_ra else sign)
    except (ValueError, TypeError):
        return None
