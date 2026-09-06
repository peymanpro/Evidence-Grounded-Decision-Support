from wealthbrain.domain.decisions import DecisionType
from wealthbrain.modules.orchestration.contracts import (
    MAX_INTERVIEW_QUESTIONS,
    AdvisoryRequest,
    OrchestrationPlan,
    ResearchTrigger,
    WorkflowStage,
)


class OrchestrationService:
    """Build a deterministic workflow without performing research or analysis."""

    _RESEARCH_SIGNALS: tuple[tuple[ResearchTrigger, tuple[str, ...]], ...] = (
        (ResearchTrigger.CURRENT_INFORMATION, ("current", "latest", "today", "right now")),
        (ResearchTrigger.MARKET_CONDITIONS, ("market conditions", "exchange rate", "inflation")),
        (ResearchTrigger.REGULATION, ("tax", "regulation", "interest rate")),
        (ResearchTrigger.IRAN_SPECIFIC, ("iran", "sanctions", "rial")),
    )

    def plan(self, request: AdvisoryRequest) -> OrchestrationPlan:
        research_triggers = self._research_triggers(request.request_text)
        stages: list[WorkflowStage] = []
        interview_budget = self._interview_budget(request)
        if interview_budget:
            stages.append(WorkflowStage.INTERVIEW)
        if research_triggers:
            stages.append(WorkflowStage.RESEARCH)
        if self._needs_quantitative_analysis(request):
            stages.append(WorkflowStage.QUANTITATIVE_ANALYSIS)
        if self._needs_risk_analysis(request):
            stages.append(WorkflowStage.RISK_ANALYSIS)
        stages.extend((WorkflowStage.CRITIQUE, WorkflowStage.SYNTHESIS))
        return OrchestrationPlan(
            stages=tuple(stages),
            interview_question_budget=interview_budget,
            research_triggers=research_triggers,
        )

    @classmethod
    def _research_triggers(cls, request_text: str) -> tuple[ResearchTrigger, ...]:
        normalized = request_text.casefold()
        return tuple(
            trigger
            for trigger, signals in cls._RESEARCH_SIGNALS
            if any(signal in normalized for signal in signals)
        )

    @staticmethod
    def _interview_budget(request: AdvisoryRequest) -> int:
        context = request.context
        missing_critical_inputs = sum(
            value is None for value in (context.capital_at_risk, context.time_horizon_months)
        )
        return min(MAX_INTERVIEW_QUESTIONS - request.questions_asked, missing_critical_inputs)

    @staticmethod
    def _needs_quantitative_analysis(request: AdvisoryRequest) -> bool:
        return request.context.decision_type in {
            DecisionType.INVESTMENT,
            DecisionType.BUSINESS,
            DecisionType.CAPITAL_ALLOCATION,
        } or request.context.capital_at_risk is not None

    @staticmethod
    def _needs_risk_analysis(request: AdvisoryRequest) -> bool:
        return request.context.decision_type is not DecisionType.OTHER
