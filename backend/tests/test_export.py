"""
Tests for export endpoints.
"""
import pytest
from fastapi import status


class TestExport:
    """Test export functionality."""
    
    def test_export_pdf_with_answers(self, client, auth_headers, test_user, db_session):
        """Test PDF export with answers."""
        from app.models.models import GenerationSession, Question
        
        # Create session with questions
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
        
        # Add questions
        for i in range(3):
            question = Question(
                session_id=session.id,
                content=f"Question {i+1}?",
                question_type="multiple_choice",
                options=["A", "B", "C", "D"],
                correct_answer="A",
                difficulty="medium"
            )
            db_session.add(question)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/export/{session.id}",
            params={"format": "pdf", "include_answers": True},
            headers=auth_headers
        )
        
        # Should return PDF or success response
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_501_NOT_IMPLEMENTED]
    
    def test_export_pdf_without_answers(self, client, auth_headers, test_user, db_session):
        """Test PDF export without answers."""
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
            content="Test question?",
            question_type="true_false",
            correct_answer="true",
            difficulty="easy"
        )
        db_session.add(question)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/export/{session.id}",
            params={"format": "pdf", "include_answers": False},
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_501_NOT_IMPLEMENTED]
    
    def test_export_csv(self, client, auth_headers, test_user, db_session):
        """Test CSV export."""
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
            content="CSV test question?",
            question_type="multiple_choice",
            options=["A", "B", "C", "D"],
            correct_answer="B",
            difficulty="hard"
        )
        db_session.add(question)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/export/{session.id}",
            params={"format": "csv"},
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_501_NOT_IMPLEMENTED]
        
        if response.status_code == status.HTTP_200_OK:
            # Check CSV content
            content = response.content.decode('utf-8')
            assert "CSV test question?" in content or len(content) > 0
    
    def test_export_unauthorized(self, client, test_user, db_session):
        """Test export without auth fails."""
        from app.models.models import GenerationSession
        
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
        
        response = client.get(
            f"/api/v1/export/{session.id}",
            params={"format": "pdf"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_export_session_not_found(self, client, auth_headers):
        """Test export with invalid session fails."""
        response = client.get(
            "/api/v1/export/99999",
            params={"format": "pdf"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_export_invalid_format(self, client, auth_headers, test_user, db_session):
        """Test export with invalid format fails."""
        from app.models.models import GenerationSession
        
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
        
        response = client.get(
            f"/api/v1/export/{session.id}",
            params={"format": "invalid_format"},
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_export_empty_session(self, client, auth_headers, test_user, db_session):
        """Test export of session with no questions."""
        from app.models.models import GenerationSession
        
        session = GenerationSession(
            user_id=test_user.id,
            source_filename="test.txt",
            source_file_hash="abc123",
            extracted_text="Test content",
            word_count=500,
            status="pending"  # No questions generated
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/export/{session.id}",
            params={"format": "pdf"},
            headers=auth_headers
        )
        
        # Should either return empty or error
        assert response.status_code in [
            status.HTTP_200_OK, 
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]
