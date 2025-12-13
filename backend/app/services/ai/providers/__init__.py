# Importa e registra todos os provedores
from app.services.ai.providers.openai_provider import OpenAIProvider
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.services.ai.providers.claude_provider import ClaudeProvider
from app.services.ai.providers.ollama_provider import OllamaProvider
from app.services.ai.providers.mock_provider import MockProvider

__all__ = ['OpenAIProvider', 'GeminiProvider', 'ClaudeProvider', 'OllamaProvider', 'MockProvider']
