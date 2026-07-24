from __future__ import annotations

import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from .base import SourceBase
from ..models import Candidate

URL = "https://www.astronomy.ohio-state.edu/asassn/transients.html"
FLOAT_RE = re.compile(r"^[+\-]?\d+(?:\.\d+)?$")

class ASASSNSource(SourceBase):
    name = "ASAS-SN"

    def fetch(self) -> list[Candidate]:
        response = self.client.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        candidates: list[Candidate] = []
        for row in soup.select("tr"):
            cells = [" ".join(cell.stripped_strings) for cell in row.find_all(["td", "th"])]
            if not cells or not any("ASASSN" in cell.upper() for cell in cells):
                continue
            name = next(cell for cell in cells if "ASASSN" in cell.upper()).split()[0]
            numbers = [float(cell) for cell in cells if FLOAT_RE.match(cell)]
            ra = numbers[0] if numbers and 0 <= numbers[0] <= 360 else None
            dec = numbers[1] if len(numbers) > 1 and -90 <= numbers[1] <= 90 else None
            mag = next((x for x in numbers[2:] if 5 <= x <= 25), None)
            text = " | ".join(cells)
            link = row.find("a", href=True)
            url = response.url.join(link["href"]) if link else URL
            candidates.append(Candidate(
                source=self.name, source_id=name, name=name, ra_deg=ra, dec_deg=dec,
                magnitude=mag, discovery_time=datetime.now(timezone.utc),
                url=str(url), comments=text, raw={"cells": cells},
            ))
        return candidates
