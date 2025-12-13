"""
Provedor Ollama para geração de questões (100% Local e Gratuito)
Requer Ollama instalado: https://ollama.ai
"""
import re
from typing import List, Optional
import structlog
import httpx

from app.core.config import settings
from app.services.ai.base import (
    AIProvider, AIProviderFactory, GeneratedQuestion, 
    GenerationParameters, QuestionType, DifficultyLevel
)

logger = structlog.get_logger()


class OllamaProvider(AIProvider):
    """
    Provedor de IA usando Ollama (local, gratuito)
    
    Modelos recomendados:
    - llama3.2 (3B) - Leve, roda em qualquer PC
    - llama3.1 (8B) - Melhor qualidade
    - mistral (7B) - Bom equilíbrio
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2"
    ):
        self.base_url = base_url
        self.model = model
        self._client = None
    
    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(base_url=self.base_url, timeout=120.0)
        return self._client
    
    @property
    def name(self) -> str:
        return "ollama"
    
    def is_available(self) -> bool:
        """Verifica se Ollama está rodando"""
        try:
            response = self.client.get("/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                return self.model in model_names or any(self.model in n for n in model_names)
            return False
        except Exception as e:
            logger.warning("ollama_not_available", error=str(e))
            return False
    
    def generate_questions(
        self, 
        context: str, 
        parameters: GenerationParameters
    ) -> List[GeneratedQuestion]:
        """Gera questões usando Ollama"""
        
        questions = []
        distribution = self._calculate_distribution(parameters)
        
        logger.info(
            "ollama_generation_started",
            model=self.model,
            total_questions=parameters.num_questions
        )
        
        for q_type, difficulty, count in distribution:
            for _ in range(count):
                try:
                    question = self._generate_single_question(
                        context, q_type, difficulty,
                        parameters.topics_filter[0] if parameters.topics_filter else ""
                    )
                    if question:
                        questions.append(question)
                except Exception as e:
                    logger.error(
                        "ollama_question_generation_failed",
                        error=str(e)
                    )
        
        logger.info(
            "ollama_generation_completed",
            generated=len(questions)
        )
        
        return questions
    
    def _calculate_distribution(self, parameters: GenerationParameters) -> List[tuple]:
        """Calcula distribuição de questões"""
        distribution = []
        total = parameters.num_questions
        types = parameters.question_types
        difficulties = parameters.difficulty_distribution
        
        per_type = total // len(types)
        remainder = total % len(types)
        
        for i, q_type in enumerate(types):
            type_count = per_type + (1 if i < remainder else 0)
            for diff_name, ratio in difficulties.items():
                diff_count = int(type_count * ratio)
                if diff_count > 0:
                    distribution.append((q_type, DifficultyLevel(diff_name), diff_count))
        
        return distribution
    
    def _generate_single_question(
        self,
        context: str,
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        topic: str
    ) -> Optional[GeneratedQuestion]:
        """Gera uma única questão"""
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_question_prompt(context, question_type, difficulty, topic)
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            response = self.client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1500
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                return self._parse_response(
                    response_text, question_type, difficulty, topic, context
                )
            
            return None
            
        except Exception as e:
            logger.error("ollama_api_error", error=str(e))
            return None
    
    def _parse_response(
        self,
        response: str,
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        topic: str,
        context: str
    ) -> Optional[GeneratedQuestion]:
        """Parse da resposta"""
        # Reutiliza parsers do OpenAI
        from app.services.ai.providers.openai_provider import OpenAIProvider
        
        parser = OpenAIProvider.__new__(OpenAIProvider)
        
        if question_type == QuestionType.MULTIPLA_ESCOLHA:
            return parser._parse_multiple_choice(response, difficulty, topic, context)
        elif question_type == QuestionType.VERDADEIRO_FALSO:
            return parser._parse_true_false(response, difficulty, topic, context)
        elif question_type == QuestionType.DISSERTATIVA:
            return parser._parse_essay(response, difficulty, topic, context)
        
        return None


# Registra o provedor
AIProviderFactory.register("ollama", OllamaProvider)
