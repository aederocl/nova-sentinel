from __future__ import annotations

from datetime import datetime, timezone
from .coords import galactic_latitude
from .models import Candidate
from .config import Settings


def score_candidate(candidate: Candidate, settings: Settings) -> Candidate:
    text = f"{candidate.name} {candidate.comments}".lower()
    score = 0
    reasons: list[str] = []

    if "nova" in text or "pnv" in text:
        score += 35; reasons.append("explicit nova/PNV language")
    if candidate.name.upper().startswith(("PNV", "TCP")):
        score += 15; reasons.append("PNV/TCP candidate identifier")
    if candidate.ra_deg is not None and candidate.dec_deg is not None:
        b = galactic_latitude(candidate.ra_deg, candidate.dec_deg)
        if abs(b) <= settings.max_galactic_latitude:
            score += 15; reasons.append(f"low Galactic latitude (b={b:.1f}°)")
    if candidate.magnitude is not None and candidate.magnitude <= settings.max_alert_magnitude:
        score += 10; reasons.append(f"bright enough (mag {candidate.magnitude:.1f})")
    if candidate.discovery_time:
        age_hours = (datetime.now(timezone.utc) - candidate.discovery_time.astimezone(timezone.utc)).total_seconds() / 3600
        if age_hours <= 24:
            score += 10; reasons.append("reported within 24 hours")
    if not any(term in text for term in ("host galaxy", "redshift", "near nucleus")):
        score += 10; reasons.append("no obvious host/redshift language")
    if any(term in text for term in ("supernova", " sn ", "agn", "tde")):
        score -= 30; reasons.append("extragalactic-transient language")
    if any(term in text for term in ("asteroid", "minor planet", "comet", "moving object")):
        score -= 20; reasons.append("moving-object language")

    candidate.score = score
    candidate.reasons = reasons
    return candidate
