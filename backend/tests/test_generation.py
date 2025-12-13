"""
Tests for question generation endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


class TestQuestionGeneration:
    """Test question generation endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_questions_success(self, client, auth_headers, test_user, db_session):
        """Test successful question generation."""
        from app.models.models import GenerationSession
        
        # Create a test session
        session = GenerationSession(
            user_id=test_user.id,
            source_filename="test.txt",
            source_file_hash="abc123",
            extracted_text="Python é uma linguagem de programação de alto nível. " * 100,
            word_count=600,
            status="pending"
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        # Mock the AI provider
        with patch('app.services.ai.question_service.QuestionService.generate_questions') as mock_gen:
            mock_gen.return_value = [
                {
                    "content": "O que é Python?",
                    "question_type": "multiple_choice",
                    "options": ["Uma cobra", "Uma linguagem", "Um framework", "Um banco de dados"],
                    "correct_answer": "Uma linguagem",
                    "justification": "Python é uma linguagem de programação.",
                    "difficulty": "easy",
                    "topic": "Python"
                }
            ]
            
            response = client.post(
                f"/api/v1/generation/{session.id}/generate",
                json={
                    "question_count": 5,
                    "question_types": ["multiple_choice"]
                },
                headers=auth_headers
            )
        
        # Should return success or processing
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
    
    def test_generate_questions_unauthorized(self, client):
        """Test generation without auth fails."""
        response = client.post(
            "/api/v1/generation/1/generate",
            json={"question_count": 5}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_generate_questions_session_not_found(self, client, auth_headers):
        """Test generation with invalid session fails."""
        response = client.post(
            "/api/v1/generation/99999/generate",
            json={"question_count": 5},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_generate_questions_invalid_count(self, client, auth_headers, test_user, db_session):
        """Test generation with invalid question count fails."""
        from app.models.models import GenerationSession
        
        session = GenerationSession(
            user_id=test_user.id,
            source_filename="test.txt",
            source_file_hash="abc123",
            extracted_text="Test content " * 100,
            word_count=200,
            status="pending"
        )
        db_session.add(session)
        db_session.commit()
        
        # Try to generate more than 20 questions
        response = client.post(
            f"/api/v1/generation/{session.id}/generate",
            json={"question_count": 50},  # Exceeds limit
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestQuestionManagement:
    """Test question CRUD operations."""
    
    def test_get_questions(self, client, auth_headers, test_user, db_session):
        """Test getting questions for a session."""
        from app.models.models import GenerationSession, Question
        
        # Create session and questions
        session = GenerationSession(
            user_id=test_user.id,
            source_filename="test.txt",
            source_file_hash="abc123",
            extracted_text="Test content",
            word_count=500,
            status="completed"
        )
        db_session.add(session)
        db_session.commit()
        
        question = Question(
            session_id=session.id,
            content="Test question?",
            question_type="multiple_choice",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            difficulty="easy"
        )
        db_session.add(question)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/generation/{session.id}/questions",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_update_question(self, client, auth_headers, test_user, db_session):
        """Test updating a question."""
        from app.models.models import GenerationSession, Question
        
        session = GenerationSession(
            user_id=test_user.id,
            source_filename="test.txt",
            source_file_hash="abc123",
            extracted_text="Test content",
            word_count=500,
            status="completed"
        )
        db_session.add(session)
        db_session.commit()
        
        question = Question(
            session_id=session.id,
            content="Original question?",
            question_type="multiple_choice",
            options=["A", "B", "C", "D"],
            correct_answer="A",
            difficulty="easy"
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        response = client.put(
            f"/api/v1/generation/questions/{question.id}",
            json={"content": "Updated question?"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Updated question?"
    
    def test_delete_question(self, client, auth_headers, test_user, db_session):
        """Test deleting a question."""
        from app.models.models import GenerationSession, Question
        
        session = GenerationSession(
            user_id=test_user.id,
            source_filename="test.txt",
            source_file_hash="abc123",
            extracted_text="Test content",
            word_count=500,
            status="completed"
        )
        db_session.add(session)
        db_session.commit()
        
        question = Question(
            session_id=session.id,
            content="To be deleted?",
            question_type="true_false",
            correct_answer="true",
            difficulty="medium"
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        
        response = client.delete(
            f"/api/v1/generation/questions/{question.id}",
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]


class TestSessionManagement:
    """Test session management endpoints."""
    
    def test_get_sessions(self, client, auth_headers, test_user, db_session):
        """Test getting user sessions."""
        from app.models.models import GenerationSession
        
        # Create some sessions
        for i in range(3):
            session = GenerationSession(
                user_id=test_user.id,
                source_filename=f"test{i}.txt",
                source_file_hash=f"hash{i}",
                extracted_text="Test content",
                word_count=500,
                status="completed"
            )
            db_session.add(session)
        db_session.commit()
        
        response = client.get("/api/v1/generation/sessions", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    def test_get_session_by_id(self, client, auth_headers, test_user, db_session):
        """Test getting a specific session."""
        from app.models.models import GenerationSession
        
        session = GenerationSession(
            user_id=test_user.id,
            source_filename="test.txt",
            source_file_hash="abc123",
            extracted_text="Test content",
            word_count=500,
            status="pending"
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        response = client.get(
            f"/api/v1/generation/{session.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == session.id
        assert data["source_filename"] == "test.txt"
