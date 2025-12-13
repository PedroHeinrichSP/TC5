"""
Rotas de exportação de questões
"""
import io
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, GenerationSession, Question, QuestionType
from app.api.routes.auth import get_current_user
from app.schemas import ExportOptions

router = APIRouter(prefix="/export", tags=["Exportação"])


def generate_pdf_content(
    questions: List[Question],
    include_answers: bool = True,
    include_justification: bool = True,
    title: str = "Avaliação"
) -> bytes:
    """
    Gera conteúdo PDF das questões
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leftIndent=20
    )
    
    option_style = ParagraphStyle(
        'Option',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=40,
        spaceAfter=5
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=10,
        textColor='green',
        leftIndent=40,
        spaceBefore=10,
        spaceAfter=5
    )
    
    elements = []
    
    # Título
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Questões
    for i, question in enumerate(questions, 1):
        # Número e enunciado
        q_text = f"<b>Questão {i}</b> ({question.difficulty.value.upper()}) - {question.topic or 'Geral'}"
        elements.append(Paragraph(q_text, styles['Heading3']))
        elements.append(Paragraph(question.content, question_style))
        
        # Alternativas para múltipla escolha
        if question.question_type == QuestionType.MULTIPLA_ESCOLHA:
            if question.option_a:
                elements.append(Paragraph(f"A) {question.option_a}", option_style))
            if question.option_b:
                elements.append(Paragraph(f"B) {question.option_b}", option_style))
            if question.option_c:
                elements.append(Paragraph(f"C) {question.option_c}", option_style))
            if question.option_d:
                elements.append(Paragraph(f"D) {question.option_d}", option_style))
        
        # Resposta e justificativa (se solicitado)
        if include_answers:
            elements.append(Paragraph(f"<b>Resposta:</b> {question.correct_answer}", answer_style))
            
            if include_justification and question.justification:
                elements.append(Paragraph(f"<b>Justificativa:</b> {question.justification}", answer_style))
        
        elements.append(Spacer(1, 20))
    
    # Se não incluir respostas, adiciona gabarito no final
    if not include_answers:
        elements.append(PageBreak())
        elements.append(Paragraph("GABARITO", title_style))
        for i, question in enumerate(questions, 1):
            elements.append(Paragraph(f"Questão {i}: {question.correct_answer}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_content(
    questions: List[Question],
    include_answers: bool = True,
    include_justification: bool = True
) -> str:
    """
    Gera conteúdo CSV das questões
    """
    import csv
    
    output = io.StringIO()
    
    headers = ['ID', 'Tipo', 'Dificuldade', 'Tópico', 'Enunciado']
    
    # Adiciona colunas de opções para múltipla escolha
    headers.extend(['Opção A', 'Opção B', 'Opção C', 'Opção D'])
    
    if include_answers:
        headers.append('Resposta Correta')
    if include_justification:
        headers.append('Justificativa')
    
    writer = csv.writer(output)
    writer.writerow(headers)
    
    for question in questions:
        row = [
            question.id,
            question.question_type.value,
            question.difficulty.value,
            question.topic or '',
            question.content
        ]
        
        # Opções
        row.extend([
            question.option_a or '',
            question.option_b or '',
            question.option_c or '',
            question.option_d or ''
        ])
        
        if include_answers:
            row.append(question.correct_answer)
        if include_justification:
            row.append(question.justification or '')
        
        writer.writerow(row)
    
    return output.getvalue()


def generate_txt_content(
    questions: List[Question],
    include_answers: bool = True,
    include_justification: bool = True,
    title: str = "Avaliação"
) -> str:
    """
    Gera conteúdo TXT das questões
    """
    lines = []
    lines.append(f"{'='*60}")
    lines.append(title.center(60))
    lines.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}".center(60))
    lines.append(f"{'='*60}")
    lines.append("")
    
    for i, question in enumerate(questions, 1):
        lines.append(f"QUESTÃO {i} [{question.difficulty.value.upper()}] - {question.topic or 'Geral'}")
        lines.append("-" * 40)
        lines.append(question.content)
        lines.append("")
        
        if question.question_type == QuestionType.MULTIPLA_ESCOLHA:
            if question.option_a:
                lines.append(f"  A) {question.option_a}")
            if question.option_b:
                lines.append(f"  B) {question.option_b}")
            if question.option_c:
                lines.append(f"  C) {question.option_c}")
            if question.option_d:
                lines.append(f"  D) {question.option_d}")
            lines.append("")
        
        if include_answers:
            lines.append(f"RESPOSTA: {question.correct_answer}")
            
            if include_justification and question.justification:
                lines.append(f"JUSTIFICATIVA: {question.justification}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("")
    
    return "\n".join(lines)


@router.post("/session/{session_id}")
async def export_session(
    session_id: int,
    options: ExportOptions,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exporta questões de uma sessão
    
    Formatos suportados: pdf, csv, txt
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
    
    # Filtra questões
    questions = session.questions
    
    if options.questions_ids:
        questions = [q for q in questions if q.id in options.questions_ids]
    
    # Filtra apenas aprovadas
    questions = [q for q in questions if q.is_approved]
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma questão aprovada para exportar"
        )
    
    # Ordena
    order_map = {
        'difficulty': lambda q: ['facil', 'medio', 'dificil'].index(q.difficulty.value),
        'topic': lambda q: q.topic or '',
        'type': lambda q: q.question_type.value,
        'id': lambda q: q.id
    }
    questions = sorted(questions, key=order_map.get(options.order_by, order_map['id']))
    
    # Gera conteúdo
    filename = f"questoes_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    title = f"Avaliação - {session.source_filename}"
    
    if options.format == "pdf":
        content = generate_pdf_content(
            questions,
            options.include_answers,
            options.include_justification,
            title
        )
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}.pdf"}
        )
    
    elif options.format == "csv":
        content = generate_csv_content(
            questions,
            options.include_answers,
            options.include_justification
        )
        return StreamingResponse(
            io.StringIO(content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
        )
    
    elif options.format == "txt":
        content = generate_txt_content(
            questions,
            options.include_answers,
            options.include_justification,
            title
        )
        return StreamingResponse(
            io.StringIO(content),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}.txt"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de exportação não suportado"
        )
