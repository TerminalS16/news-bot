import logging

from anthropic import Anthropic

from bot.config import settings
from llm_providers.base import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)

    def complete(self, prompt: str) -> str:
        response = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "max_tokens":
            logger.warning("Ответ модели обрезан по лимиту max_tokens")
        return response.content[0].text