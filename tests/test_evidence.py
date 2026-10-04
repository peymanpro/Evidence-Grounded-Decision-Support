from datetime import UTC, datetime
from uuid import uuid4

from wealthbrain.modules.decisions.contracts import (
    EvidenceProvenance,
    EvidenceResponse,
)
from wealthbrain.modules.evidence.service import assess_sufficiency


def evidence(
    *,
    domain: str,
    quality: str = "unverified",
    supports: bool = True,
    with_hash: bool = True,
) -> EvidenceResponse:
    provenance = EvidenceProvenance(
        publisher="Example",
        retrieved_at=datetime.now(UTC),
        status_code=200,
        content_type="text/html",
        content_sha256=(
            "0" * 64
            if with_hash
            else None
        ),
        content_length_bytes=100,
    )
    return EvidenceResponse(
        id=uuid4(),
        decision_id=uuid4(),
        title="Evidence",
        source_url=f"https://{domain}/article",
        claim="A test claim.",
        supports=supports,
        confidence=0.9,
        quality=quality,
        provenance=provenance,
        created_at=datetime.now(UTC),
    )


def test_verified_supporting_evidence_from_two_domains_is_sufficient() -> None:
    result = assess_sufficiency(
        [
            evidence(domain="alpha.example", quality="verified"),
            evidence(domain="beta.example", quality="verified"),
        ]
    )

    assert result.sufficient is True
    assert result.verified_supporting_count == 2
    assert result.source_domain_count == 2
    assert result.score == 1.0
    assert result.blocking_issues == []


def test_unverified_supporting_evidence_is_not_sufficient_for_automation() -> None:
    result = assess_sufficiency(
        [evidence(domain="alpha.example", quality="unverified")]
    )

    assert result.sufficient is False
    assert any("verified quality state" in item for item in result.blocking_issues)


def test_missing_retrieval_hash_is_blocking() -> None:
    result = assess_sufficiency(
        [evidence(domain="alpha.example", quality="verified", with_hash=False)]
    )

    assert result.sufficient is False
    assert any("content hash" in item for item in result.blocking_issues)


def test_challenging_evidence_is_reported_as_warning() -> None:
    result = assess_sufficiency(
        [
            evidence(domain="alpha.example", quality="verified"),
            evidence(
                domain="beta.example",
                quality="challenged",
                supports=False,
            ),
        ]
    )

    assert result.challenging_count == 1
    assert any("challenging evidence" in item for item in result.warnings)
