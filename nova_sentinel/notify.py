from __future__ import annotations

import html
import json
from pathlib import Path
import httpx
from .config import Settings
from .models import Candidate


def format_alert(c: Candidate) -> str:
    coords = "unknown coordinates"
    if c.ra_deg is not None and c.dec_deg is not None:
        coords = f"RA={c.ra_deg:.5f}°, Dec={c.dec_deg:+.5f}°"
    mag = f"mag≈{c.magnitude:.1f}" if c.magnitude is not None else "magnitude unknown"
    reasons = "; ".join(c.reasons)
    return f"NOVA CANDIDATE ALERT — score {c.score}\n{c.name} ({c.source})\n{coords}; {mag}\n{reasons}\n{c.url or ''}"


def deliver(c: Candidate, settings: Settings) -> None:
    message = format_alert(c)
    print(message, flush=True)
    with Path(settings.jsonl_path).open("a", encoding="utf-8") as stream:
        stream.write(c.to_json() + "\n")
    if settings.telegram_bot_token and settings.telegram_chat_id:
        httpx.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": message, "disable_web_page_preview": False},
            timeout=settings.timeout,
        ).raise_for_status()
    if settings.webhook_url:
        httpx.post(settings.webhook_url, json=c.to_dict(), timeout=settings.timeout).raise_for_status()


def write_atom(rows, path: str) -> None:
    entries = []
    for row in rows:
        link = html.escape(row["url"] or "")
        title = html.escape(f'{row["name"]} — score {row["score"]}')
        content = html.escape(row["comments"] or "")
        entries.append(f"""<entry><id>urn:sha256:{row['fingerprint']}</id><title>{title}</title><updated>{row['last_seen']}</updated><link href=\"{link}\"/><content>{content}</content></entry>""")
    updated = rows[0]["last_seen"] if rows else "1970-01-01T00:00:00+00:00"
    xml = f'''<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><id>urn:nova-sentinel</id><title>Nova Sentinel alerts</title><updated>{updated}</updated>{''.join(entries)}</feed>'''
    Path(path).write_text(xml, encoding="utf-8")
