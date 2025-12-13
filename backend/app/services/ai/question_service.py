"""
Serviço principal de geração de questões
Orquestra todo o pipeline de geração
"""
import time
import hashlib
from typing import List, Optional, Dict, Any
from dataclasses import asdict
import structlog

from app.core.config import settings
from app.services.ai.text_extractor import TextExtractor, ContentValidator
from app.services.ai.topic_segmenter import TopicSegmenter
from app.services.ai.difficulty_classifier import DifficultyClassifier
from app.services.ai.base import (
    AIProviderFactory, GenerationParameters, GeneratedQuestion,
    QuestionType, DifficultyLevel
)
# Importa providers para registrá-los na factory
from app.services.ai import providers

logger = structlog.get_logger()


class QuestionGenerationService:
    """
    Serviço principal que orquestra o pipeline completo de geração:
    1. Extração de texto
    2. Validação de conteúdo
    3. Segmentação de tópicos
    4. Geração via IA
    5. Classificação de dificuldade
    6. Validação de qualidade
    """
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.content_validator = ContentValidator(min_words=settings.min_content_words)
        self.topic_segmenter = TopicSegmenter()
        self.difficulty_classifier = DifficultyClassifier()
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Processa arquivo e extrai conteúdo
        
        Returns:
            Dict com texto extraído e análise de conteúdo
        """
        logger.info("file_processing_started", file=file_path)
        
        # Extrai texto
        text = self.text_extractor.extract(file_path)
        
        # Valida conteúdo
        validation = self.content_validator.validate(text)
        
        # Gera hash do conteúdo
        content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        return {
            'text': text,
            'content_hash': content_hash,
            'validation': validation,
            'preview': text[:500] + '...' if len(text) > 500 else text
        }
    
    def analyze_topics(self, text: str) -> List[Dict[str, Any]]:
        """
        Analisa e segmenta o texto em tópicos
        
        Returns:
            Lista de tópicos identificados com keywords
        """
        segments = self.topic_segmenter.segment(text)
        
        return [
            {
                'topic': seg.topic,
                'keywords': seg.keywords,
                'relevance_score': seg.relevance_score,
                'word_count': len(seg.content.split())
            }
            for seg in segments
        ]
    
    def generate_questions(
        self,
        text: str,
        parameters: GenerationParameters,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera questões usando o pipeline completo
        
        Args:
            text: Texto fonte para geração
            parameters: Parâmetros de geração
            provider_name: Nome do provedor de IA (opcional, usa configuração padrão)
            
        Returns:
            Dict com questões geradas e metadados
        """
        start_time = time.time()
        
        # Determina provedor
        provider_name = provider_name or parameters.ai_provider or settings.ai_provider
        
        logger.info(
            "question_generation_started",
            provider=provider_name,
            num_questions=parameters.num_questions,
            question_types=[qt.value for qt in parameters.question_types]
        )
        
        # Segmenta conteúdo em tópicos
        segments = self.topic_segmenter.segment(text)
        
        # Prepara contexto otimizado
        context_parts = []
        for seg in segments[:3]:  # Usa top 3 tópicos mais relevantes
            context_parts.append(f"### {seg.topic}\n{seg.content[:2000]}")
        
        optimized_context = "\n\n".join(context_parts)
        
        # Obtém provedor de IA
        try:
            provider = AIProviderFactory.create(provider_name)
        except ValueError as e:
            # Tenta fallback para outro provedor disponível
            available = AIProviderFactory.get_available_providers()
            if available:
                provider_name = available[0]
                provider = AIProviderFactory.create(provider_name)
                logger.warning("using_fallback_provider", fallback=provider_name)
            else:
                # Usa mock como último recurso para permitir testes
                logger.warning("no_provider_available_using_mock")
                provider_name = "mock"
                provider = AIProviderFactory.create("mock")
        
        # Verifica disponibilidade
        if not provider.is_available():
            available = AIProviderFactory.get_available_providers()
            if available:
                provider_name = available[0]
                provider = AIProviderFactory.create(provider_name)
                logger.warning("provider_unavailable_using_fallback", fallback=provider_name)
            else:
                # Usa mock como último recurso para permitir testes
                logger.warning("provider_unavailable_using_mock")
                provider_name = "mock"
                provider = AIProviderFactory.create("mock")
        
        # Adiciona tópicos aos parâmetros
        if not parameters.topics_filter:
            parameters.topics_filter = [seg.topic for seg in segments[:3]]
        
        # Gera questões
        generated = provider.generate_questions(optimized_context, parameters)
        
        # Classifica dificuldade de cada questão (se não foi definida pela IA)
        questions_with_difficulty = []
        for question in generated:
            # Reclassifica dificuldade se necessário
            analysis = self.difficulty_classifier.classify(
                question.content + " " + (question.justification or ""),
                optimized_context
            )
            
            # Converte para dict
            q_dict = asdict(question)
            q_dict['difficulty_analysis'] = asdict(analysis)
            
            # Usa a dificuldade classificada se muito diferente da original
            if question.difficulty.value != analysis.level:
                logger.debug(
                    "difficulty_reclassified",
                    original=question.difficulty.value,
                    new=analysis.level
                )
            
            questions_with_difficulty.append(q_dict)
        
        processing_time = time.time() - start_time
        
        logger.info(
            "question_generation_completed",
            generated=len(questions_with_difficulty),
            processing_time=processing_time
        )
        
        return {
            'questions': questions_with_difficulty,
            'metadata': {
                'provider': provider_name,
                'processing_time_seconds': round(processing_time, 2),
                'topics_used': [seg.topic for seg in segments[:3]],
                'total_generated': len(questions_with_difficulty),
                'parameters': {
                    'num_questions': parameters.num_questions,
                    'question_types': [qt.value for qt in parameters.question_types],
                    'difficulty_distribution': parameters.difficulty_distribution
                }
            }
        }
    
    def regenerate_single_question(
        self,
        text: str,
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        topic: str,
        provider_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Regenera uma única questão com parâmetros específicos
        """
        params = GenerationParameters(
            num_questions=1,
            question_types=[question_type],
            difficulty_distribution={difficulty.value: 1.0},
            topics_filter=[topic] if topic else None
        )
        
        result = self.generate_questions(text, params, provider_name)
        
        if result['questions']:
            return result['questions'][0]
        return None


# Instância singleton do serviço
question_service = QuestionGenerationService()
