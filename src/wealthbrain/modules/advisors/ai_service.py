from typing import Final
from uuid import UUID

from wealthbrain.config.settings import get_settings
from wealthbrain.modules.ai.contracts import CompletionRequest
from wealthbrain.modules.ai.factory import create_ai_provider
from wealthbrain.modules.ai.provider import AIProvider
from wealthbrain.modules.advisors.contracts import AdvisorResponse, AdvisorRole
from wealthbrain.modules.decisions.service import DecisionService


ROLE_INSTRUCTIONS: Final[dict[AdvisorRole, str]] = {
    "evidence": (
        "Audit evidence provenance, source quality, contradictions, and missing "
        "support. Do not invent sources."
    ),
    "quantitative": (
        "Inspect criteria, weights, score coverage, and sensitivity. Identify "
        "assumptions that could reverse the ranking."
    ),
    "risk": (
        "Stress-test downside scenarios, uncertainty, exposure, and mitigation. "
        "Do not recommend autonomous external actions."
    ),
    "challenge": (
        "Argue against the leading conclusion. Find plausible alternatives, "
        "hidden assumptions, and evidence that would change the decision."
    ),
}


class ModelAdvisorService:
    def __init__(
        self,
        decision_service: DecisionService,
        provider: AIProvider | None = None,
    ) -> None:
        self._decision_service = decision_service
        self._provider = provider

    async def review(
        self,
        decision_id: UUID,
        role: AdvisorRole,
        max_tokens: int = 1_500,
    ) -> AdvisorResponse:
        report = await self._decision_service.report(decision_id)
        settings = get_settings()
        provider = self._provider or create_ai_provider(settings)
        response = await provider.complete(
            CompletionRequest(
                system_prompt=(
                    "You are a specialist advisor inside WealthBrain. "
                    "Return cautious, inspectable reasoning. Distinguish "
                    "evidence from assumptions and state uncertainty explicitly. "
                    "Never claim professional financial advice or execute actions.\n\n"
                    f"Specialist role: {role}\n"
                    f"Role instruction: {ROLE_INSTRUCTIONS[role]}"
                ),
                user_prompt=report.model_dump_json(indent=2),
                model=settings.default_ai_model,
                max_tokens=max_tokens,
            )
        )
        return AdvisorResponse(
            role=role,
            provider=response.provider,
            model=response.model,
            content=response.content,
            human_review_required=True,
        )
