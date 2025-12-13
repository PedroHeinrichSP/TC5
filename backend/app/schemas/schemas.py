"""
Schemas Pydantic para validação de dados
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ===== ENUMS =====

class DifficultyLevel(str, Enum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class QuestionType(str, Enum):
    MULTIPLA_ESCOLHA = "multipla_escolha"
    VERDADEIRO_FALSO = "verdadeiro_falso"
    DISSERTATIVA = "dissertativa"


# ===== USER SCHEMAS =====

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


# ===== QUESTION SCHEMAS =====

class QuestionBase(BaseModel):
    question_type: QuestionType
    content: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: str
    justification: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIO
    topic: Optional[str] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[str] = None
    justification: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    topic: Optional[str] = None
    is_approved: Optional[bool] = None


class QuestionResponse(QuestionBase):
    id: int
    session_id: int
    quality_score: Optional[float] = None
    factuality_score: Optional[float] = None
    source_excerpt: Optional[str] = None
    is_edited: bool
    is_approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== GENERATION SCHEMAS =====

class GenerationParams(BaseModel):
    """Parâmetros para geração de questões"""
    num_questions: int = Field(default=10, ge=1, le=20)
    question_types: List[QuestionType] = Field(
        default=[QuestionType.MULTIPLA_ESCOLHA, QuestionType.VERDADEIRO_FALSO]
    )
    difficulty_distribution: Optional[dict] = Field(
        default={"facil": 0.3, "medio": 0.5, "dificil": 0.2}
    )
    topics_filter: Optional[List[str]] = None
    ai_provider: Optional[str] = None  # openai | gemini | claude


class GenerationSessionResponse(BaseModel):
    id: int
    user_id: int
    source_filename: Optional[str]
    word_count: Optional[int]
    status: str
    ai_provider: Optional[str]
    parameters: Optional[dict]
    processing_time_seconds: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    questions: List[QuestionResponse] = []
    
    class Config:
        from_attributes = True


class GenerationSessionList(BaseModel):
    id: int
    source_filename: Optional[str]
    status: str
    question_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== CONTENT ANALYSIS =====

class ContentAnalysis(BaseModel):
    """Resultado da análise de conteúdo"""
    word_count: int
    language: str
    topics: List[str]
    is_sufficient: bool
    suggestions: Optional[List[str]] = None


class TopicSegment(BaseModel):
    """Segmento de texto com tópico identificado"""
    topic: str
    content: str
    keywords: List[str]
    relevance_score: float


# ===== API RESPONSES =====

class APIResponse(BaseModel):
    """Resposta padrão da API"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Resposta de erro da API"""
    status: str = "error"
    message: str
    errors: Optional[List[str]] = None


# ===== EXPORT =====

class ExportOptions(BaseModel):
    """Opções de exportação"""
    format: str = Field(default="pdf", pattern="^(pdf|csv|txt)$")
    include_answers: bool = True
    include_justification: bool = True
    order_by: str = Field(default="difficulty", pattern="^(difficulty|topic|type|id)$")
    questions_ids: Optional[List[int]] = None  # Se None, exporta todas
