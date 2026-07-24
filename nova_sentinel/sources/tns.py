from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from .base import SourceBase
from ..models import Candidate

URL = "https://www.wis-tns.org/api/get/search"

class TNSSource(SourceBase):
    name = "TNS"

    def fetch(self) -> list[Candidate]:
        s = self.settings
        if not (s.tns_bot_id and s.tns_bot_name and s.tns_api_key):
            return []
        marker = json.dumps({"tns_id": int(s.tns_bot_id), "type": "bot", "name": s.tns_bot_name})
        headers = {"User-Agent": f"tns_marker{marker}", "Accept": "application/json"}
        payload = {
            "api_key": s.tns_api_key,
            "data": json.dumps({
                "public_timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "num_page": "100",
            }),
        }
        response = self.client.post(URL, data=payload, headers=headers)
        response.raise_for_status()
        body = response.json()
        rows = body.get("data", {}).get("reply", [])
        result: list[Candidate] = []
        for row in rows:
            name = row.get("objname") or row.get("name") or "TNS candidate"
            result.append(Candidate(
                source=self.name,
                source_id=str(name),
                name=str(name),
                ra_deg=_float(row.get("radeg")),
                dec_deg=_float(row.get("decdeg")),
                magnitude=_float(row.get("discoverymag")),
                discovery_time=_date(row.get("discoverydate")),
                url=f"https://www.wis-tns.org/object/{name}",
                comments=" ".join(str(row.get(k, "")) for k in ("name_prefix", "type", "internal_names")),
                raw=row,
            ))
        return result

def _float(value):
    try: return float(value)
    except (TypeError, ValueError): return None

def _date(value):
    if not value: return None
    try: return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
    except ValueError: return None
