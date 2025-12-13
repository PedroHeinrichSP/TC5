"""
Modelos SQLAlchemy do sistema
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class DifficultyLevel(str, enum.Enum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class QuestionType(str, enum.Enum):
    MULTIPLA_ESCOLHA = "multipla_escolha"
    VERDADEIRO_FALSO = "verdadeiro_falso"
    DISSERTATIVA = "dissertativa"


class User(Base):
    """Modelo de usuário do sistema"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    sessions = relationship("GenerationSession", back_populates="user")


class GenerationSession(Base):
    """Sessão de geração de questões"""
    __tablename__ = "generation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadados do arquivo fonte
    source_filename = Column(String(255))
    source_file_hash = Column(String(64))
    content_preview = Column(Text)  # Primeiros 500 caracteres
    word_count = Column(Integer)
    
    # Parâmetros de geração
    ai_provider = Column(String(50))
    parameters = Column(JSON)  # Parâmetros usados na geração
    
    # Status e timestamps
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    processing_time_seconds = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relacionamentos
    user = relationship("User", back_populates="sessions")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")


class Question(Base):
    """Questão gerada pelo sistema"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("generation_sessions.id"), nullable=False)
    
    # Conteúdo da questão
    question_type = Column(Enum(QuestionType), nullable=False)
    content = Column(Text, nullable=False)  # Enunciado da questão
    
    # Para múltipla escolha
    option_a = Column(Text)
    option_b = Column(Text)
    option_c = Column(Text)
    option_d = Column(Text)
    
    # Resposta e justificativa
    correct_answer = Column(String(10))  # "A", "B", "C", "D", "V", "F" ou texto para dissertativa
    justification = Column(Text)
    
    # Classificação
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIO)
    topic = Column(String(255))  # Tópico identificado
    
    # Scores de qualidade
    quality_score = Column(Float)
    factuality_score = Column(Float)
    
    # Metadados
    source_excerpt = Column(Text)  # Trecho do texto fonte usado
    is_edited = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    session = relationship("GenerationSession", back_populates="questions")


class QuestionEdit(Base):
    """Histórico de edições de questões"""
    __tablename__ = "question_edits"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    field_changed = Column(String(50))  # content, options, answer, difficulty, etc.
    old_value = Column(Text)
    new_value = Column(Text)
    
    edited_at = Column(DateTime, default=datetime.utcnow)
