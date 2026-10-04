from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID

from pydantic import BaseModel

from wealthbrain.modules.decisions.contracts import DecisionReport
from wealthbrain.modules.evaluation.contracts import DecisionQualityReport


class EvaluationArtifact(BaseModel):
    artifact_version: str = "1.0"
    decision_id: UUID
    generated_at: datetime
    report: DecisionReport
    quality: DecisionQualityReport
    deterministic: bool = True
    external_model_calls: bool = False
    evaluation_input_sha256: str


def build_evaluation_artifact(
    report: DecisionReport,
    quality: DecisionQualityReport,
) -> EvaluationArtifact:
    stable_payload = {
        "report": report.model_dump(mode="json"),
        "quality": quality.model_dump(mode="json"),
    }
    serialized = repr(stable_payload).encode("utf-8")
    return EvaluationArtifact(
        decision_id=report.decision.id,
        generated_at=datetime.now(UTC),
        report=report,
        quality=quality,
        evaluation_input_sha256=sha256(serialized).hexdigest(),
    )
