from collections.abc import Sequence
from urllib.parse import urlsplit

from wealthbrain.modules.decisions.contracts import EvidenceResponse
from wealthbrain.modules.evidence.contracts import EvidenceSufficiency


def assess_sufficiency(
    evidence: Sequence[EvidenceResponse],
) -> EvidenceSufficiency:
    supporting = [item for item in evidence if item.supports]
    challenging = [item for item in evidence if not item.supports]
    verified_supporting = [
        item for item in supporting if item.quality == "verified"
    ]

    domains = {
        urlsplit(str(item.source_url)).hostname
        for item in evidence
        if urlsplit(str(item.source_url)).hostname
    }

    score = (
        min(1.0, len(supporting) / 2.0) * 0.4
        + (
            len(verified_supporting) / len(supporting)
            if supporting
            else 0.0
        )
        * 0.4
        + min(1.0, len(domains) / 2.0) * 0.2
    )

    blocking_issues: list[str] = []
    warnings: list[str] = []

    if not supporting:
        blocking_issues.append("No supporting evidence is recorded.")
    if supporting and not verified_supporting:
        blocking_issues.append(
            "No supporting evidence has an explicit verified quality state."
        )
    if supporting and not any(
        item.provenance.content_sha256 for item in supporting
    ):
        blocking_issues.append(
            "Supporting evidence has no retrieval content hash."
        )
    if len(domains) < 2 and evidence:
        warnings.append("Evidence currently relies on fewer than two source domains.")
    if challenging:
        warnings.append(
            f"{len(challenging)} challenging evidence item(s) should be considered."
        )

    sufficient = score >= 0.75 and not blocking_issues
    return EvidenceSufficiency(
        supporting_count=len(supporting),
        challenging_count=len(challenging),
        verified_supporting_count=len(verified_supporting),
        source_domain_count=len(domains),
        score=round(score, 6),
        sufficient=sufficient,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )
