from datetime import datetime, timezone
from nova_sentinel.config import Settings
from nova_sentinel.models import Candidate
from nova_sentinel.scoring import score_candidate


def test_explicit_nova_scores_highly():
    c = Candidate(source="test", source_id="PNV-test", name="PNV-test", ra_deg=266.4,
                  dec_deg=-29.0, magnitude=12.0, discovery_time=datetime.now(timezone.utc),
                  comments="possible nova candidate")
    score_candidate(c, Settings())
    assert c.score >= 45


def test_asteroid_is_penalized():
    c = Candidate(source="test", source_id="x", name="x", comments="probable asteroid moving object")
    score_candidate(c, Settings())
    assert c.score < 0
