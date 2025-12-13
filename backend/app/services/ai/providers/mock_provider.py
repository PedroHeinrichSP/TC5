"""
Provedor Mock para testes - gera questões de exemplo sem usar IA real
"""
import random
from typing import List
import structlog

from app.services.ai.base import (
    AIProvider, AIProviderFactory, GeneratedQuestion, 
    GenerationParameters, QuestionType, DifficultyLevel
)

logger = structlog.get_logger()


class MockProvider(AIProvider):
    """Provedor Mock que gera questões de exemplo para testes"""
    
    def __init__(self):
        pass
    
    @property
    def name(self) -> str:
        return "mock"
    
    def is_available(self) -> bool:
        """Sempre disponível"""
        return True
    
    def generate_questions(
        self, 
        context: str, 
        parameters: GenerationParameters
    ) -> List[GeneratedQuestion]:
        """Gera questões mock baseadas no contexto"""
        
        logger.info("mock_generation_started", num_questions=parameters.num_questions)
        
        questions = []
        
        # Extrai algumas palavras-chave do contexto para tornar as questões mais relevantes
        words = context.split()[:100]
        keywords = [w for w in words if len(w) > 5][:10]
        topic = keywords[0] if keywords else "Conceito"
        
        for i in range(parameters.num_questions):
            # Alterna tipos de questões baseado na configuração
            if parameters.question_types:
                q_type = parameters.question_types[i % len(parameters.question_types)]
            else:
                q_type = QuestionType.MULTIPLA_ESCOLHA
            
            # Determina dificuldade
            difficulties = list(DifficultyLevel)
            difficulty = random.choice(difficulties)
            
            if q_type == QuestionType.MULTIPLA_ESCOLHA:
                question = self._generate_multiple_choice(i + 1, topic, difficulty, context)
            elif q_type == QuestionType.VERDADEIRO_FALSO:
                question = self._generate_true_false(i + 1, topic, difficulty, context)
            else:
                question = self._generate_essay(i + 1, topic, difficulty, context)
            
            questions.append(question)
        
        logger.info("mock_generation_completed", questions_count=len(questions))
        return questions
    
    def _generate_multiple_choice(
        self, num: int, topic: str, difficulty: DifficultyLevel, context: str
    ) -> GeneratedQuestion:
        """Gera questão de múltipla escolha"""
        return GeneratedQuestion(
            question_type=QuestionType.MULTIPLA_ESCOLHA,
            content=f"Questao {num}: Com base no conteudo apresentado sobre {topic}, qual das alternativas abaixo melhor descreve o conceito principal?",
            options={
                "A": f"A primeira caracteristica importante de {topic} e sua aplicacao pratica no contexto academico.",
                "B": f"A segunda perspectiva sobre {topic} enfatiza aspectos teoricos fundamentais.",
                "C": f"Uma visao alternativa de {topic} que considera fatores secundarios.",
                "D": f"Uma interpretacao incorreta que confunde {topic} com conceitos relacionados."
            },
            correct_answer="A",
            justification=f"A alternativa A esta correta pois descreve adequadamente a aplicacao pratica de {topic} conforme apresentado no texto. As demais alternativas apresentam interpretacoes parciais ou incorretas do conceito.",
            difficulty=difficulty,
            topic=topic,
            source_excerpt=context[:200] if context else ""
        )
    
    def _generate_true_false(
        self, num: int, topic: str, difficulty: DifficultyLevel, context: str
    ) -> GeneratedQuestion:
        """Gera questão verdadeiro/falso"""
        is_true = num % 2 == 0
        return GeneratedQuestion(
            question_type=QuestionType.VERDADEIRO_FALSO,
            content=f"Questao {num}: Verdadeiro ou Falso - O conceito de {topic} apresentado no texto estabelece que sua principal caracteristica e a aplicabilidade em contextos diversos.",
            options=None,
            correct_answer="Verdadeiro" if is_true else "Falso",
            justification=f"A afirmacao e {'verdadeira' if is_true else 'falsa'} porque o texto {'confirma' if is_true else 'contradiz'} essa interpretacao ao apresentar {topic} de forma {'abrangente' if is_true else 'especifica'}.",
            difficulty=difficulty,
            topic=topic,
            source_excerpt=context[:200] if context else ""
        )
    
    def _generate_essay(
        self, num: int, topic: str, difficulty: DifficultyLevel, context: str
    ) -> GeneratedQuestion:
        """Gera questão dissertativa"""
        return GeneratedQuestion(
            question_type=QuestionType.DISSERTATIVA,
            content=f"Questao {num}: Discorra sobre os principais aspectos de {topic} apresentados no texto, relacionando-os com sua aplicacao pratica no contexto academico brasileiro.",
            options=None,
            correct_answer="Resposta dissertativa esperada",
            justification=f"A resposta deve abordar: 1) Definicao de {topic}; 2) Principais caracteristicas; 3) Aplicacoes praticas; 4) Relevancia no contexto brasileiro. Espera-se argumentacao coerente e fundamentada no texto.",
            difficulty=difficulty,
            topic=topic,
            source_excerpt=context[:200] if context else ""
        )


# Registra o provedor na factory
AIProviderFactory.register("mock", MockProvider)
