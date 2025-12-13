"""
Provedor Google Gemini para geração de questões
"""
import re
from typing import List, Optional
import structlog
import google.generativeai as genai

from app.core.config import settings
from app.services.ai.base import (
    AIProvider, AIProviderFactory, GeneratedQuestion, 
    GenerationParameters, QuestionType, DifficultyLevel
)

logger = structlog.get_logger()


class GeminiProvider(AIProvider):
    """Provedor de IA usando Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash-lite"):
        self.api_key = api_key or settings.google_api_key
        self.model_name = model
        self._model = None
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    @property
    def model(self):
        if self._model is None:
            self._model = genai.GenerativeModel(self.model_name)
        return self._model
    
    @property
    def name(self) -> str:
        return "gemini"
    
    def is_available(self) -> bool:
        """Verifica se a API está disponível"""
        if not self.api_key or self.api_key.startswith("sua-"):
            return False
        try:
            # Teste simples
            self.model.generate_content("Olá")
            return True
        except Exception as e:
            logger.warning("gemini_not_available", error=str(e))
            return False
    
    def generate_questions(
        self, 
        context: str, 
        parameters: GenerationParameters
    ) -> List[GeneratedQuestion]:
        """Gera questões usando Gemini"""
        
        questions = []
        distribution = self._calculate_distribution(parameters)
        
        logger.info(
            "gemini_generation_started",
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
                        "gemini_question_generation_failed",
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
        
        prompt = self._build_system_prompt() + "\n\n" + \
                 self._build_question_prompt(context, question_type, difficulty, topic)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1500
                )
            )
            
            return self._parse_response(
                response.text, question_type, difficulty, topic, context
            )
            
        except Exception as e:
            logger.error("gemini_api_error", error=str(e))
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
        # Reutiliza a mesma lógica de parsing
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
AIProviderFactory.register("gemini", GeminiProvider)
