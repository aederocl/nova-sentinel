# Nova Sentinel

A small, shareable service for monitoring public transient feeds and producing rapid alerts for plausible nova eruptions.

Nova Sentinel watches upstream candidate streams rather than waiting for a formal nova classification. It currently supports:

- CBAT Transient Objects Confirmation Page (TOCP)
- ASAS-SN public transient table
- TNS API (optional; credentials required)
- Generic JSON feeds for local/community adapters

Candidates are normalized, deduplicated in SQLite, assigned a transparent nova-interest score, and published to:

- console and structured JSONL
- an Atom feed (`feed.xml`)
- Telegram (optional)
- a generic webhook (optional)

> **Scientific caution**: an alert means “worth checking promptly,” not “confirmed nova.” Expect dwarf novae, young stellar objects, microlensing events, asteroids, artifacts, and extragalactic transients among the candidates.

## Quick start

```bash
git clone https://github.com/YOUR-ORG/nova-sentinel.git
cd nova-sentinel
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
nova-sentinel run
```

The default configuration writes `nova_sentinel.db`, `alerts.jsonl`, and `feed.xml` in the working directory.

## Configuration

Settings are read from environment variables or a `.env` file.

```dotenv
POLL_MINUTES=10
MIN_ALERT_SCORE=45
MAX_GALACTIC_LATITUDE=20
MAX_ALERT_MAGNITUDE=18

# Optional TNS bot credentials
TNS_BOT_ID=
TNS_BOT_NAME=
TNS_API_KEY=

# Optional Telegram delivery
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Optional generic POST endpoint
WEBHOOK_URL=
```

TNS access requires a registered bot and API key. Do not commit credentials.

## One-shot and continuous modes

```bash
nova-sentinel check        # fetch once
nova-sentinel run          # repeat using POLL_MINUTES
nova-sentinel rebuild-feed # rebuild Atom feed from the database
```

For a small server or Raspberry Pi, use the included Docker Compose file. GitHub Actions is also included as a demonstration, but hosted cron jobs may run late; a continuously running machine is preferable for genuinely prompt follow-up.

## Scoring

The default score is intentionally interpretable:

- +35: source/comment explicitly says nova or PNV
- +15: TCP/PNV-style candidate name
- +15: within configured Galactic-latitude limit
- +10: brighter than configured magnitude limit
- +10: recent report
- +10: no obvious host/redshift language
- −30: explicit supernova/AGN/TDE language
- −20: explicit moving-object/asteroid/comet language

Thresholds and weights are easy to change in `nova_sentinel/scoring.py`. The score is a triage device, not a probabilistic classification.

## Adding another source

Create a class under `nova_sentinel/sources/` implementing:

```python
class MySource:
    name = "my-source"

    def fetch(self) -> list[Candidate]:
        ...
```

Then register it in `nova_sentinel/app.py`. Preserve the source URL and as much original text as possible.

## Suggested operational workflow

1. Alert on plausible *young Galactic transients*, not only confirmed novae.
2. Open the source report immediately.
3. Check coordinates, discovery image, previous non-detection, known counterpart, and moving-object contamination.
4. Inspect recent photometry where available.
5. Estimate visibility from the intended observatory.
6. Trigger spectroscopy under your institution’s own observing and safety procedures.
7. Publish a classification through the appropriate community channel.

## Data ethics and etiquette

- Respect source rate limits and terms of use.
- Identify your bot where an API requires it.
- Do not redistribute private mailing-list messages without permission.
- Attribute discovery reports and observers.
- Avoid claiming discovery or classification from an automated alert alone.

## License

MIT. See `LICENSE`.
