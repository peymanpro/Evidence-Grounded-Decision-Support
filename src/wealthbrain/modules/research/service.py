from collections.abc import Sequence

from wealthbrain.modules.research.contracts import (
    ResearchFinding,
    ResearchPlan,
    ResearchQuestion,
)


class ResearchService:
    """Provider-neutral research orchestration boundary.

    Search/fetch providers can be added later without coupling the decision
    domain to a specific search vendor.
    """

    def build_plan(
        self,
        decision_id: str,
        questions: Sequence[ResearchQuestion],
    ) -> ResearchPlan:
        return ResearchPlan(decision_id=decision_id, questions=list(questions), findings=[])

    def attach_findings(
        self,
        plan: ResearchPlan,
        findings: Sequence[ResearchFinding],
    ) -> ResearchPlan:
        return plan.model_copy(update={"findings": list(findings)})
