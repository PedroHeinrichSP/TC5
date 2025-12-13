"""
Provedor OpenAI para geração de questões
"""
import re
from typing import List, Optional
import structlog
from openai import OpenAI

from app.core.config import settings
from app.services.ai.base import (
    AIProvider, AIProviderFactory, GeneratedQuestion, 
    GenerationParameters, QuestionType, DifficultyLevel
)

logger = structlog.get_logger()


class OpenAIProvider(AIProvider):
    """Provedor de IA usando OpenAI GPT"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self._client = None
    
    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    @property
    def name(self) -> str:
        return "openai"
    
    def is_available(self) -> bool:
        """Verifica se a API está disponível"""
        if not self.api_key or self.api_key.startswith("sk-sua-"):
            return False
        try:
            # Teste simples de conectividade
            self.client.models.list()
            return True
        except Exception as e:
            logger.warning("openai_not_available", error=str(e))
            return False
    
    def generate_questions(
        self, 
        context: str, 
        parameters: GenerationParameters
    ) -> List[GeneratedQuestion]:
        """Gera questões usando OpenAI"""
        
        questions = []
        
        # Distribui questões por tipo e dificuldade
        distribution = self._calculate_distribution(parameters)
        
        logger.info(
            "openai_generation_started",
            total_questions=parameters.num_questions,
            distribution=distribution
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
                        "openai_question_generation_failed",
                        error=str(e),
                        question_type=q_type.value
                    )
        
        logger.info(
            "openai_generation_completed",
            generated=len(questions),
            requested=parameters.num_questions
        )
        
        return questions
    
    def _calculate_distribution(
        self, 
        parameters: GenerationParameters
    ) -> List[tuple]:
        """Calcula distribuição de questões por tipo e dificuldade"""
        distribution = []
        
        total = parameters.num_questions
        types = parameters.question_types
        difficulties = parameters.difficulty_distribution
        
        # Distribui igualmente entre tipos
        per_type = total // len(types)
        remainder = total % len(types)
        
        for i, q_type in enumerate(types):
            type_count = per_type + (1 if i < remainder else 0)
            
            # Distribui por dificuldade
            for diff_name, ratio in difficulties.items():
                diff_count = int(type_count * ratio)
                if diff_count > 0:
                    difficulty = DifficultyLevel(diff_name)
                    distribution.append((q_type, difficulty, diff_count))
        
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content
            return self._parse_response(response_text, question_type, difficulty, topic, context)
            
        except Exception as e:
            logger.error("openai_api_error", error=str(e))
            return None
    
    def _parse_response(
        self,
        response: str,
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        topic: str,
        context: str
    ) -> Optional[GeneratedQuestion]:
        """Parse da resposta da IA para GeneratedQuestion"""
        
        try:
            if question_type == QuestionType.MULTIPLA_ESCOLHA:
                return self._parse_multiple_choice(response, difficulty, topic, context)
            elif question_type == QuestionType.VERDADEIRO_FALSO:
                return self._parse_true_false(response, difficulty, topic, context)
            elif question_type == QuestionType.DISSERTATIVA:
                return self._parse_essay(response, difficulty, topic, context)
        except Exception as e:
            logger.warning("parse_error", error=str(e), response_preview=response[:200])
            return None
    
    def _parse_multiple_choice(
        self, 
        response: str, 
        difficulty: DifficultyLevel,
        topic: str,
        context: str
    ) -> Optional[GeneratedQuestion]:
        """Parse de questão múltipla escolha"""
        
        # Extrai componentes usando regex
        question_match = re.search(r'QUEST[ÃA]O:\s*(.+?)(?=\nA\))', response, re.DOTALL | re.IGNORECASE)
        option_a = re.search(r'A\)\s*(.+?)(?=\nB\))', response, re.DOTALL)
        option_b = re.search(r'B\)\s*(.+?)(?=\nC\))', response, re.DOTALL)
        option_c = re.search(r'C\)\s*(.+?)(?=\nD\))', response, re.DOTALL)
        option_d = re.search(r'D\)\s*(.+?)(?=\nRESPOSTA:)', response, re.DOTALL)
        answer_match = re.search(r'RESPOSTA:\s*([A-Da-d])', response, re.IGNORECASE)
        justification_match = re.search(r'JUSTIFICATIVA:\s*(.+?)$', response, re.DOTALL | re.IGNORECASE)
        
        if not all([question_match, option_a, option_b, option_c, option_d, answer_match]):
            return None
        
        return GeneratedQuestion(
            question_type=QuestionType.MULTIPLA_ESCOLHA,
            content=question_match.group(1).strip(),
            options={
                "A": option_a.group(1).strip(),
                "B": option_b.group(1).strip(),
                "C": option_c.group(1).strip(),
                "D": option_d.group(1).strip()
            },
            correct_answer=answer_match.group(1).upper(),
            justification=justification_match.group(1).strip() if justification_match else "",
            difficulty=difficulty,
            topic=topic,
            source_excerpt=context[:500]
        )
    
    def _parse_true_false(
        self, 
        response: str, 
        difficulty: DifficultyLevel,
        topic: str,
        context: str
    ) -> Optional[GeneratedQuestion]:
        """Parse de questão verdadeiro/falso"""
        
        affirmation_match = re.search(r'AFIRMA[ÇC][ÃA]O:\s*(.+?)(?=\nRESPOSTA:)', response, re.DOTALL | re.IGNORECASE)
        answer_match = re.search(r'RESPOSTA:\s*([VFvf])', response, re.IGNORECASE)
        justification_match = re.search(r'JUSTIFICATIVA:\s*(.+?)$', response, re.DOTALL | re.IGNORECASE)
        
        if not all([affirmation_match, answer_match]):
            return None
        
        return GeneratedQuestion(
            question_type=QuestionType.VERDADEIRO_FALSO,
            content=affirmation_match.group(1).strip(),
            correct_answer=answer_match.group(1).upper(),
            justification=justification_match.group(1).strip() if justification_match else "",
            difficulty=difficulty,
            topic=topic,
            source_excerpt=context[:500]
        )
    
    def _parse_essay(
        self, 
        response: str, 
        difficulty: DifficultyLevel,
        topic: str,
        context: str
    ) -> Optional[GeneratedQuestion]:
        """Parse de questão dissertativa"""
        
        question_match = re.search(r'QUEST[ÃA]O:\s*(.+?)(?=\nRESPOSTA_ESPERADA:)', response, re.DOTALL | re.IGNORECASE)
        answer_match = re.search(r'RESPOSTA_ESPERADA:\s*(.+?)(?=\nCRIT[ÉE]RIOS:)', response, re.DOTALL | re.IGNORECASE)
        criteria_match = re.search(r'CRIT[ÉE]RIOS:\s*(.+?)$', response, re.DOTALL | re.IGNORECASE)
        
        if not question_match:
            return None
        
        justification = ""
        if answer_match:
            justification += f"Resposta Esperada:\n{answer_match.group(1).strip()}"
        if criteria_match:
            justification += f"\n\nCritérios:\n{criteria_match.group(1).strip()}"
        
        return GeneratedQuestion(
            question_type=QuestionType.DISSERTATIVA,
            content=question_match.group(1).strip(),
            correct_answer="Ver resposta esperada",
            justification=justification,
            difficulty=difficulty,
            topic=topic,
            source_excerpt=context[:500]
        )


# Registra o provedor na factory
AIProviderFactory.register("openai", OpenAIProvider)
