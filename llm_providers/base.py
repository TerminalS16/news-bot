from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Отправляет промпт и возвращает текстовый ответ модели."""