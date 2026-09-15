from llm_providers.base import LLMProvider


class FakeProvider(LLMProvider):
    """Провайдер-заглушка для тестирования без реального обращения к платному API.
    Не использовать в проде — только для проверки остального пайплайна."""

    def complete(self, prompt: str) -> str:
        return "[ТЕСТОВЫЙ ОТВЕТ] Здесь будет результат реальной ИИ-обработки."