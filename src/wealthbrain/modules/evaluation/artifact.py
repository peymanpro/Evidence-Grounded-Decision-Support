from datetime import UTC, datetime
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


def build_evaluation_artifact(
    report: DecisionReport,
    quality: DecisionQualityReport,
) -> EvaluationArtifact:
    return EvaluationArtifact(
        decision_id=report.decision.id,
        generated_at=datetime.now(UTC),
        report=report,
        quality=quality,
    )
