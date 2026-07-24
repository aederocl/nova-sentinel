from __future__ import annotations

import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from .base import SourceBase
from ..coords import parse_sexagesimal
from ..models import Candidate

URL = "https://www.cbat.eps.harvard.edu/unconf/tocp.html"
NAME_RE = re.compile(r"\b(?:PNV|TCP|PSN)\S+", re.I)
COORD_RE = re.compile(r"(\d{1,2}[: ]\d{2}[: ]\d{2}(?:\.\d+)?)\s+([+\-]\d{1,2}[: ]\d{2}[: ]\d{2}(?:\.\d+)?)")
MAG_RE = re.compile(r"\b(?:mag(?:nitude)?\s*[=:]?\s*)?(\d{1,2}(?:\.\d+)?)\s*(?:mag)?\b", re.I)

class TOCPSource(SourceBase):
    name = "CBAT-TOCP"

    def fetch(self) -> list[Candidate]:
        response = self.client.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        candidates: list[Candidate] = []
        for row in soup.select("tr"):
            text = " ".join(row.stripped_strings)
            match = NAME_RE.search(text)
            if not match:
                continue
            name = match.group(0).strip(";,()")
            coord = COORD_RE.search(text)
            ra = parse_sexagesimal(coord.group(1), True) if coord else None
            dec = parse_sexagesimal(coord.group(2), False) if coord else None
            mag_match = MAG_RE.search(text[match.end():])
            mag = float(mag_match.group(1)) if mag_match else None
            link = row.find("a", href=True)
            url = response.url.join(link["href"]) if link else URL
            candidates.append(Candidate(
                source=self.name, source_id=name, name=name, ra_deg=ra, dec_deg=dec,
                magnitude=mag, discovery_time=datetime.now(timezone.utc),
                url=str(url), comments=text, raw={"row_text": text},
            ))
        return candidates
