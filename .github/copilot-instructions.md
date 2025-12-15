# AI-Powered Academic Question Generator - Copilot Instructions

## Project Overview
This is an academic AI system that generates multiple-choice, true/false, and essay questions from PDF/text inputs for Computer Science students at PUC Minas. The project must be completed by December 14, 2025, using a modular, Docker-containerized architecture.

## Core Architecture & Design Patterns

### Layered Architecture
Follow strict separation of concerns across these layers:
- **Ingestion Layer**: File upload, text extraction, content validation
- **Processing/AI Layer**: Content segmentation, topic identification, question generation
- **Business Logic Layer**: Question classification, difficulty assessment, validation rules
- **API Layer**: RESTful endpoints for frontend communication
- **UI Layer**: React/Vue components for user interactions

### Data Flow Pattern
```
Input → Content Extraction → Topic Segmentation → AI Generation → Human Review → Export
```
Each step must preserve context and allow rollback on failure.

## Technical Conventions

### File Handling Requirements
- Support PDF (≤50 pages), TXT, DOCX formats up to 20MB
- Extract text while filtering out headers, footers, page numbers
- Implement content validation: minimum 500 words for meaningful question generation
- Store temporary files in `/tmp/uploads/` with automatic cleanup after processing

### Question Generation Standards
- **Multiple Choice**: 1 correct + 3-4 plausible distractors, avoid obvious wrong answers
- **True/False**: Include brief justification (2-3 sentences) for the correct answer  
- **Essay**: Open-ended questions with suggested answer outline/key points
- **Difficulty Classification**: Automatic assignment based on concept complexity, vocabulary level, and cognitive load

### API Design Patterns
```python
# Standard response format for all endpoints
{
  "status": "success|error",
  "data": {...},
  "metadata": {"timestamp", "processing_time", "user_id"},
  "errors": [] # only if status == "error"
}
```

### User Workflow Implementation
1. **Authentication**: Simple email/password with bcrypt hashing
2. **Generation Parameters**: Max 20 questions per request to maintain performance
3. **Preview Mode**: Always show generated questions before final export
4. **Manual Editing**: In-place editing of questions, answers, and difficulty levels
5. **Export Options**: PDF with/without answer key, CSV for data analysis

## Development Guidelines

### Performance Requirements
- Question generation: ≤60 seconds for 20 questions from 2000 words
- File processing: ≤120 seconds for 50-page PDFs
- UI response: ≤5 seconds for page loads
- Implement progress indicators for operations >10 seconds

### Testing Strategy
- Unit tests: ≥40% coverage focusing on business logic
- Integration tests: End-to-end question generation workflows
- Performance tests: Load testing with maximum file sizes
- Content validation tests: Ensure generated questions match source material accuracy ≥80%

### Error Handling Patterns
```python
# Preserve user data on failures
try:
    questions = generate_questions(content, params)
except ContentInsufficientError:
    return suggest_content_expansion(content, params)
except AIServiceError:
    return retry_with_fallback_model(content, params)
```

### Docker & Deployment
- Single-command deployment: `docker-compose up --build`
- Environment variables for AI model selection (local vs. API)
- Separate containers for web app, AI processing, and database
- Volume mounts for persistent user data and logs

## AI Integration Specifics

### Model Flexibility
Support switching between AI providers (OpenAI, Gemini, Claude) via configuration without code changes:
```python
ai_provider = config.get('AI_PROVIDER', 'openai')
generator = QuestionGeneratorFactory.create(ai_provider)
```

### Content Processing Pipeline
1. **Text Cleaning**: Remove formatting artifacts, normalize whitespace
2. **Topic Extraction**: Identify 3-5 main concepts per 1000 words
3. **Context Windows**: Segment long documents while preserving topic coherence
4. **Quality Validation**: Reject questions that don't reference source material

### Privacy & Ethics
- Display AI usage warnings prominently
- Never store user content beyond processing session
- Implement data deletion on user request
- Log generation metadata for academic evaluation only

## Database Schema Patterns
```sql
-- User sessions and history
sessions: user_id, upload_timestamp, source_file_hash, question_count, parameters
questions: session_id, type, difficulty, content, correct_answer, justification
user_edits: question_id, field_changed, old_value, new_value, timestamp
```

## Common Integration Points

### File Upload Component
- Drag-and-drop interface with progress bars
- Client-side file type validation before upload
- Chunked upload for large files with resume capability

### Question Review Interface  
- Side-by-side view: original content excerpt + generated question
- Inline editing with immediate validation
- Batch operations: approve/reject multiple questions
- Regenerate individual questions while maintaining context

### Export Module
- Template-based PDF generation with institutional branding
- Configurable question ordering (by difficulty, topic, type)
- Metadata inclusion: generation date, source summary, question statistics

## Development Workflow
1. Implement core question generation first (MVP)
2. Add user management and persistence
3. Build review/editing interface
4. Implement export functionality
5. Add performance optimizations and error handling
6. Docker containerization and deployment preparation

Focus on the user journey: upload → generate → review → export. Each step must work reliably before adding advanced features.