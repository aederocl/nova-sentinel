from __future__ import annotations

import logging
from .config import Settings
from .db import Store
from .notify import deliver, write_atom
from .scoring import score_candidate
from .sources.asassn import ASASSNSource
from .sources.tocp import TOCPSource
from .sources.tns import TNSSource

log = logging.getLogger(__name__)


def check_once(settings: Settings) -> dict[str, int]:
    store = Store(settings.database_path)
    sources = [TOCPSource(settings), ASASSNSource(settings), TNSSource(settings)]
    fetched = alerts = errors = 0
    for source in sources:
        try:
            candidates = source.fetch()
            fetched += len(candidates)
            for candidate in candidates:
                score_candidate(candidate, settings)
                is_new, score_increased = store.upsert(candidate)
                if candidate.score >= settings.min_alert_score and (is_new or score_increased):
                    deliver(candidate, settings)
                    store.mark_alerted(candidate.fingerprint)
                    alerts += 1
        except Exception:
            errors += 1
            log.exception("Source failed: %s", source.name)
    write_atom(store.recent(), settings.atom_path)
    return {"fetched": fetched, "alerts": alerts, "errors": errors}
