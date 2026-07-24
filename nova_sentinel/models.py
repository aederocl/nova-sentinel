from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json


@dataclass(slots=True)
class Candidate:
    source: str
    source_id: str
    name: str
    ra_deg: float | None = None
    dec_deg: float | None = None
    magnitude: float | None = None
    discovery_time: datetime | None = None
    url: str | None = None
    comments: str = ""
    raw: dict = field(default_factory=dict)
    score: int = 0
    reasons: list[str] = field(default_factory=list)

    @property
    def fingerprint(self) -> str:
        if self.ra_deg is not None and self.dec_deg is not None:
            key = f"sky:{self.ra_deg:.4f}:{self.dec_deg:.4f}"
        else:
            key = f"id:{self.source}:{self.source_id or self.name}"
        return hashlib.sha256(key.encode()).hexdigest()

    def to_dict(self) -> dict:
        value = asdict(self)
        value["fingerprint"] = self.fingerprint
        value["discovery_time"] = (
            self.discovery_time.astimezone(timezone.utc).isoformat()
            if self.discovery_time else None
        )
        return value

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)
