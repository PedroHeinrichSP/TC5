"""
Interface abstrata e Factory para provedores de IA
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()


class QuestionType(str, Enum):
    MULTIPLA_ESCOLHA = "multipla_escolha"
    VERDADEIRO_FALSO = "verdadeiro_falso"
    DISSERTATIVA = "dissertativa"


class DifficultyLevel(str, Enum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


@dataclass
class GeneratedQuestion:
    """Questão gerada pela IA"""
    question_type: QuestionType
    content: str
    options: Optional[Dict[str, str]] = None  # {"A": "...", "B": "...", etc}
    correct_answer: str = ""
    justification: str = ""
    difficulty: DifficultyLevel = DifficultyLevel.MEDIO
    topic: str = ""
    source_excerpt: str = ""


@dataclass
class GenerationParameters:
    """Parâmetros para geração de questões"""
    num_questions: int = 10
    question_types: List[QuestionType] = None
    difficulty_distribution: Dict[str, float] = None
    topics_filter: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.question_types is None:
            self.question_types = [QuestionType.MULTIPLA_ESCOLHA]
        if self.difficulty_distribution is None:
            self.difficulty_distribution = {"facil": 0.3, "medio": 0.5, "dificil": 0.2}


class AIProvider(ABC):
    """Interface abstrata para provedores de IA"""
    
    @abstractmethod
    def generate_questions(
        self, 
        context: str, 
        parameters: GenerationParameters
    ) -> List[GeneratedQuestion]:
        """Gera questões baseadas no contexto"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provedor está disponível"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do provedor"""
        pass
    
    def _build_system_prompt(self) -> str:
        """Prompt de sistema base para todos os provedores"""
        return """Você é um especialista em criação de questões acadêmicas para o ensino superior brasileiro.
Sua tarefa é gerar questões de alta qualidade baseadas no conteúdo fornecido.

REGRAS IMPORTANTES:
1. Todas as questões DEVEM ser baseadas EXCLUSIVAMENTE no conteúdo fornecido
2. NÃO invente informações que não estejam no texto
3. Use linguagem acadêmica formal em português brasileiro
4. Para múltipla escolha: crie distratores plausíveis mas claramente incorretos
5. Sempre forneça justificativa para a resposta correta
6. Adapte a complexidade ao nível de dificuldade solicitado"""
    
    def _build_question_prompt(
        self, 
        context: str, 
        question_type: QuestionType,
        difficulty: DifficultyLevel,
        topic: str = ""
    ) -> str:
        """Constrói prompt específico para tipo de questão"""
        
        prompts = {
            QuestionType.MULTIPLA_ESCOLHA: f"""
CONTEXTO:
{context}

TÓPICO: {topic if topic else 'Geral'}
DIFICULDADE: {difficulty.value.upper()}

Gere UMA questão de MÚLTIPLA ESCOLHA seguindo este formato EXATO:

QUESTÃO: [enunciado claro e objetivo]
A) [alternativa A]
B) [alternativa B]
C) [alternativa C]
D) [alternativa D]
RESPOSTA: [apenas a letra: A, B, C ou D]
JUSTIFICATIVA: [explicação de 2-3 frases do porquê a resposta está correta]

Regras:
- O enunciado deve ser claro e sem ambiguidade
- Apenas UMA alternativa deve estar correta
- Distratores devem ser plausíveis mas incorretos
- Nível {difficulty.value}: {"conceitos básicos e definições" if difficulty == DifficultyLevel.FACIL else "aplicação e análise" if difficulty == DifficultyLevel.MEDIO else "síntese e avaliação crítica"}
""",
            
            QuestionType.VERDADEIRO_FALSO: f"""
CONTEXTO:
{context}

TÓPICO: {topic if topic else 'Geral'}
DIFICULDADE: {difficulty.value.upper()}

Gere UMA questão de VERDADEIRO ou FALSO seguindo este formato EXATO:

AFIRMAÇÃO: [uma afirmação clara que pode ser verdadeira ou falsa]
RESPOSTA: [apenas V ou F]
JUSTIFICATIVA: [explicação de 2-3 frases justificando a resposta]

Regras:
- A afirmação deve ser objetiva e verificável no contexto
- Evite afirmações obviamente verdadeiras ou falsas
- Nível {difficulty.value}: {"afirmações diretas do texto" if difficulty == DifficultyLevel.FACIL else "inferências moderadas" if difficulty == DifficultyLevel.MEDIO else "análise crítica de conceitos"}
""",
            
            QuestionType.DISSERTATIVA: f"""
CONTEXTO:
{context}

TÓPICO: {topic if topic else 'Geral'}
DIFICULDADE: {difficulty.value.upper()}

Gere UMA questão DISSERTATIVA seguindo este formato EXATO:

QUESTÃO: [pergunta aberta que exige resposta elaborada]
RESPOSTA_ESPERADA: [pontos principais que devem constar na resposta - em tópicos]
CRITÉRIOS: [critérios de avaliação da resposta]

Regras:
- A questão deve estimular análise e reflexão
- A resposta esperada deve listar 3-5 pontos principais
- Nível {difficulty.value}: {"descrição e explicação" if difficulty == DifficultyLevel.FACIL else "comparação e aplicação" if difficulty == DifficultyLevel.MEDIO else "avaliação e proposta de soluções"}
"""
        }
        
        return prompts.get(question_type, prompts[QuestionType.MULTIPLA_ESCOLHA])


class AIProviderFactory:
    """Factory para criação de provedores de IA"""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type):
        """Registra um novo provedor"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> AIProvider:
        """Cria instância do provedor especificado"""
        if provider_name not in cls._providers:
            available = list(cls._providers.keys())
            raise ValueError(
                f"Provedor '{provider_name}' não encontrado. "
                f"Disponíveis: {available}"
            )
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Retorna lista de provedores disponíveis e funcionais"""
        available = []
        for name, provider_class in cls._providers.items():
            try:
                provider = provider_class()
                if provider.is_available():
                    available.append(name)
            except Exception:
                pass
        return available
