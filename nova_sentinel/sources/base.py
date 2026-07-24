from __future__ import annotations

import httpx
from ..config import Settings

class SourceBase:
    name = "base"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = httpx.Client(
            timeout=settings.timeout,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        )

    def fetch(self):
        raise NotImplementedError
