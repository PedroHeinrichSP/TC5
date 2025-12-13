"""
Rotas de upload e processamento de arquivos
"""
import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models import User, GenerationSession
from app.api.routes.auth import get_current_user
from app.services.ai import question_service
from app.schemas import ContentAnalysis, APIResponse

router = APIRouter(prefix="/upload", tags=["Upload"])


def ensure_upload_dir():
    """Garante que o diretório de upload existe"""
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Extrai extensão do arquivo"""
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def validate_file(file: UploadFile) -> None:
    """Valida arquivo antes do upload"""
    # Valida extensão
    extension = get_file_extension(file.filename)
    if extension not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado. Formatos aceitos: {settings.allowed_extensions}"
        )
    
    # Valida tamanho (precisa ler o arquivo)
    file.file.seek(0, 2)  # Vai para o fim
    size = file.file.tell()
    file.file.seek(0)  # Volta para o início
    
    if size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Máximo: {settings.max_file_size_mb}MB"
        )


@router.post("/file", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Faz upload de um arquivo e extrai seu conteúdo
    
    Retorna análise do conteúdo e ID da sessão para geração
    """
    ensure_upload_dir()
    validate_file(file)
    
    # Gera nome único para o arquivo
    file_hash = hashlib.md5(f"{current_user.id}_{file.filename}".encode()).hexdigest()[:12]
    extension = get_file_extension(file.filename)
    temp_filename = f"{file_hash}.{extension}"
    temp_path = os.path.join(settings.upload_dir, temp_filename)
    
    try:
        # Salva arquivo temporariamente
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Processa arquivo
        result = question_service.process_file(temp_path)
        
        # Cria sessão de geração
        session = GenerationSession(
            user_id=current_user.id,
            source_filename=file.filename,
            source_file_hash=result['content_hash'],
            content_preview=result['preview'],
            word_count=result['validation']['word_count'],
            status="pending"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Analisa tópicos
        topics = question_service.analyze_topics(result['text'])
        
        return {
            "status": "success",
            "data": {
                "session_id": session.id,
                "filename": file.filename,
                "content_hash": result['content_hash'],
                "analysis": result['validation'],
                "topics": topics,
                "preview": result['preview']
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )
    finally:
        # Remove arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/text", response_model=dict)
async def upload_text(
    content: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recebe texto diretamente (copy/paste)
    
    Retorna análise do conteúdo e ID da sessão para geração
    """
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conteúdo não pode estar vazio"
        )
    
    # Valida conteúdo
    from app.services.ai import ContentValidator
    validator = ContentValidator(min_words=settings.min_content_words)
    validation = validator.validate(content)
    
    # Gera hash do conteúdo
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    # Cria sessão
    session = GenerationSession(
        user_id=current_user.id,
        source_filename="texto_colado",
        source_file_hash=content_hash,
        content_preview=content[:500] + '...' if len(content) > 500 else content,
        word_count=validation['word_count'],
        status="pending"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Analisa tópicos
    topics = question_service.analyze_topics(content)
    
    return {
        "status": "success",
        "data": {
            "session_id": session.id,
            "content_hash": content_hash,
            "analysis": validation,
            "topics": topics,
            "preview": content[:500] + '...' if len(content) > 500 else content
        }
    }
