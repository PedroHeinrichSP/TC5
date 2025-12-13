"""
Provedor Anthropic Claude para geração de questões
"""
import re
from typing import List, Optional
import structlog
from anthropic import Anthropic

from app.core.config import settings
from app.services.ai.base import (
    AIProvider, AIProviderFactory, GeneratedQuestion, 
    GenerationParameters, QuestionType, DifficultyLevel
)

logger = structlog.get_logger()


class ClaudeProvider(AIProvider):
    """Provedor de IA usando Anthropic Claude"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model
        self._client = None
    
    @property
    def client(self) -> Anthropic:
        if self._client is None:
            self._client = Anthropic(api_key=self.api_key)
        return self._client
    
    @property
    def name(self) -> str:
        return "claude"
    
    def is_available(self) -> bool:
        """Verifica se a API está disponível"""
        if not self.api_key or self.api_key.startswith("sk-ant-sua-"):
            return False
        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Olá"}]
            )
            return True
        except Exception as e:
            logger.warning("claude_not_available", error=str(e))
            return False
    
    def generate_questions(
        self, 
        context: str, 
        parameters: GenerationParameters
    ) -> List[GeneratedQuestion]:
        """Gera questões usando Claude"""
        
        questions = []
        distribution = self._calculate_distribution(parameters)
        
        logger.info(
            "claude_generation_started",
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
                        "claude_question_generation_failed",
                        error=str(e)
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
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            response_text = response.content[0].text
            return self._parse_response(
                response_text, question_type, difficulty, topic, context
            )
            
        except Exception as e:
            logger.error("claude_api_error", error=str(e))
            return None
    
    def _parse_response(
        self,
        response: str,
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        topic: str,
        context: str
    ) -> Optional[GeneratedQuestion]:
        """Parse da resposta similar ao OpenAI"""
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
AIProviderFactory.register("claude", ClaudeProvider)
