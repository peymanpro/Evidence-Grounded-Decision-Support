from uuid import UUID

from wealthbrain.config.settings import get_settings
from wealthbrain.modules.ai.contracts import CompletionRequest
from wealthbrain.modules.ai.factory import create_ai_provider
from wealthbrain.modules.decisions.service import DecisionService


class DecisionAIService:
    def __init__(self, decision_service: DecisionService) -> None:
        self._decision_service = decision_service

    async def critique(self, decision_id: UUID) -> str:
        report = await self._decision_service.report(decision_id)
        settings = get_settings()
        provider = create_ai_provider(settings)
        response = await provider.complete(
            CompletionRequest(
                system_prompt=(
                    "Analyze the supplied decision report as a cautious reasoning assistant. "
                    "Separate evidence, assumptions, uncertainty, and risks. "
                    "Do not execute actions and do not present certainty unsupported by the report."
                ),
                user_prompt=report.model_dump_json(indent=2),
                model=settings.default_ai_model,
                max_tokens=2000,
            )
        )
        return response.content
