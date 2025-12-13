"""
Rotas de geração de questões
"""
import os
import hashlib
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models import User, GenerationSession, Question, DifficultyLevel, QuestionType
from app.api.routes.auth import get_current_user
from app.services.ai import question_service, GenerationParameters
from app.services.ai.base import QuestionType as AIQuestionType, DifficultyLevel as AIDifficultyLevel
from app.schemas import (
    GenerationParams, QuestionResponse, QuestionUpdate,
    GenerationSessionResponse, GenerationSessionList, APIResponse
)

router = APIRouter(prefix="/generation", tags=["Geração"])


def save_questions_to_db(
    db: Session,
    session: GenerationSession,
    questions_data: List[dict]
) -> List[Question]:
    """Salva questões geradas no banco de dados"""
    questions = []
    
    for q_data in questions_data:
        question = Question(
            session_id=session.id,
            question_type=QuestionType(q_data['question_type']),
            content=q_data['content'],
            option_a=q_data.get('options', {}).get('A'),
            option_b=q_data.get('options', {}).get('B'),
            option_c=q_data.get('options', {}).get('C'),
            option_d=q_data.get('options', {}).get('D'),
            correct_answer=q_data['correct_answer'],
            justification=q_data.get('justification', ''),
            difficulty=DifficultyLevel(q_data['difficulty']),
            topic=q_data.get('topic', ''),
            quality_score=q_data.get('difficulty_analysis', {}).get('score'),
            source_excerpt=q_data.get('source_excerpt', '')[:1000]
        )
        db.add(question)
        questions.append(question)
    
    db.commit()
    for q in questions:
        db.refresh(q)
    
    return questions


@router.post("/{session_id}/generate", response_model=dict)
async def generate_questions(
    session_id: int,
    params: GenerationParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera questões para uma sessão existente
    """
    # Busca sessão
    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    if session.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sessão já está em processamento"
        )
    
    # Valida número de questões
    if params.num_questions > settings.max_questions_per_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Máximo de {settings.max_questions_per_request} questões por requisição"
        )
    
    # Atualiza status
    session.status = "processing"
    session.ai_provider = params.ai_provider or settings.ai_provider
    session.parameters = {
        "num_questions": params.num_questions,
        "question_types": [qt.value for qt in params.question_types],
        "difficulty_distribution": params.difficulty_distribution
    }
    db.commit()
    
    try:
        # Converte parâmetros
        ai_params = GenerationParameters(
            num_questions=params.num_questions,
            question_types=[AIQuestionType(qt.value) for qt in params.question_types],
            difficulty_distribution=params.difficulty_distribution,
            topics_filter=params.topics_filter
        )
        
        # Gera questões (usa o preview como texto, em produção usaria o texto completo armazenado)
        # Em uma implementação real, o texto seria armazenado na sessão ou em cache
        text_content = session.content_preview  # Simplificado para demonstração
        
        result = question_service.generate_questions(
            text_content,
            ai_params,
            session.ai_provider
        )
        
        # Salva questões no banco
        questions = save_questions_to_db(db, session, result['questions'])
        
        # Atualiza sessão
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.processing_time_seconds = result['metadata']['processing_time_seconds']
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "session_id": session.id,
                "questions_generated": len(questions),
                "metadata": result['metadata'],
                "questions": [
                    {
                        "id": q.id,
                        "type": q.question_type.value,
                        "content": q.content,
                        "options": {
                            "A": q.option_a,
                            "B": q.option_b,
                            "C": q.option_c,
                            "D": q.option_d
                        } if q.question_type == QuestionType.MULTIPLA_ESCOLHA else None,
                        "correct_answer": q.correct_answer,
                        "justification": q.justification,
                        "difficulty": q.difficulty.value,
                        "topic": q.topic
                    }
                    for q in questions
                ]
            }
        }
        
    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na geração: {str(e)}"
        )


@router.get("/sessions", response_model=dict)
async def list_sessions(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista sessões de geração do usuário
    """
    sessions = db.query(GenerationSession).filter(
        GenerationSession.user_id == current_user.id
    ).order_by(
        GenerationSession.created_at.desc()
    ).limit(limit).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": s.id,
                "source_filename": s.source_filename,
                "status": s.status,
                "question_count": len(s.questions),
                "created_at": s.created_at.isoformat(),
                "completed_at": s.completed_at.isoformat() if s.completed_at else None
            }
            for s in sessions
        ]
    }


@router.get("/sessions/{session_id}", response_model=dict)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna detalhes de uma sessão com suas questões
    """
    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    return {
        "status": "success",
        "data": {
            "id": session.id,
            "source_filename": session.source_filename,
            "word_count": session.word_count,
            "status": session.status,
            "ai_provider": session.ai_provider,
            "parameters": session.parameters,
            "processing_time_seconds": session.processing_time_seconds,
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "questions": [
                {
                    "id": q.id,
                    "type": q.question_type.value,
                    "content": q.content,
                    "options": {
                        "A": q.option_a,
                        "B": q.option_b,
                        "C": q.option_c,
                        "D": q.option_d
                    } if q.question_type == QuestionType.MULTIPLA_ESCOLHA else None,
                    "correct_answer": q.correct_answer,
                    "justification": q.justification,
                    "difficulty": q.difficulty.value,
                    "topic": q.topic,
                    "is_approved": q.is_approved,
                    "is_edited": q.is_edited
                }
                for q in session.questions
            ]
        }
    }


@router.get("/{session_id}/questions", response_model=List[dict])
async def get_session_questions(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna apenas as questões de uma sessão
    """
    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    return [
        {
            "id": q.id,
            "question_type": q.question_type.value,
            "content": q.content,
            "options": [q.option_a, q.option_b, q.option_c, q.option_d] if q.question_type == QuestionType.MULTIPLA_ESCOLHA else None,
            "correct_answer": q.correct_answer,
            "justification": q.justification,
            "difficulty": q.difficulty.value,
            "topic": q.topic,
            "is_approved": q.is_approved,
            "is_edited": q.is_edited
        }
        for q in session.questions
    ]


@router.put("/questions/{question_id}", response_model=dict)
async def update_question(
    question_id: int,
    update_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma questão existente
    """
    question = db.query(Question).join(GenerationSession).filter(
        Question.id == question_id,
        GenerationSession.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questão não encontrada"
        )
    
    # Atualiza campos fornecidos
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if hasattr(question, field):
            setattr(question, field, value)
    
    question.is_edited = True
    question.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(question)
    
    return {
        "status": "success",
        "message": "Questão atualizada com sucesso",
        "data": {
            "id": question.id,
            "content": question.content,
            "difficulty": question.difficulty.value,
            "is_edited": question.is_edited
        }
    }


@router.delete("/questions/{question_id}", response_model=dict)
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove uma questão
    """
    question = db.query(Question).join(GenerationSession).filter(
        Question.id == question_id,
        GenerationSession.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questão não encontrada"
        )
    
    db.delete(question)
    db.commit()
    
    return {
        "status": "success",
        "message": "Questão removida com sucesso"
    }


@router.post("/questions/{question_id}/regenerate", response_model=dict)
async def regenerate_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenera uma questão específica mantendo tipo, dificuldade e tópico
    """
    question = db.query(Question).join(GenerationSession).filter(
        Question.id == question_id,
        GenerationSession.user_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questão não encontrada"
        )
    
    session = question.session
    
    try:
        # Regenera questão
        new_question_data = question_service.regenerate_single_question(
            text=session.content_preview,
            question_type=AIQuestionType(question.question_type.value),
            difficulty=AIDifficultyLevel(question.difficulty.value),
            topic=question.topic,
            provider_name=session.ai_provider
        )
        
        if not new_question_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Não foi possível regenerar a questão"
            )
        
        # Atualiza questão existente
        question.content = new_question_data['content']
        question.correct_answer = new_question_data['correct_answer']
        question.justification = new_question_data.get('justification', '')
        
        if new_question_data.get('options'):
            question.option_a = new_question_data['options'].get('A')
            question.option_b = new_question_data['options'].get('B')
            question.option_c = new_question_data['options'].get('C')
            question.option_d = new_question_data['options'].get('D')
        
        question.is_edited = False
        question.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(question)
        
        return {
            "status": "success",
            "message": "Questão regenerada com sucesso",
            "data": {
                "id": question.id,
                "content": question.content,
                "correct_answer": question.correct_answer,
                "justification": question.justification
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao regenerar questão: {str(e)}"
        )
