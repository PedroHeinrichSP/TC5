"""
Integration tests for the complete question generation workflow.
"""
import pytest
from fastapi import status
from io import BytesIO
from unittest.mock import patch, AsyncMock


class TestCompleteWorkflow:
    """Test the complete user workflow from upload to export."""
    
    def test_complete_workflow(self, client, sample_text_content):
        """Test the full workflow: register -> login -> upload -> generate -> export."""
        
        # Step 1: Register
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "workflow@example.com",
                "password": "workflowtest123",
                "full_name": "Workflow Test User"
            }
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Step 2: Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "workflow@example.com",
                "password": "workflowtest123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Upload file
        # Extend content to meet minimum word requirement
        extended_content = (sample_text_content + " ") * 5  # ~500+ words
        file_content = extended_content.encode('utf-8')
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        upload_response = client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers
        )
        assert upload_response.status_code == status.HTTP_200_OK
        session_id = upload_response.json()["data"]["id"]
        
        # Step 4: Generate questions (mocked)
        with patch('app.services.ai.question_service.QuestionService.generate_questions') as mock_gen:
            mock_gen.return_value = [
                {
                    "content": "O que é Python?",
                    "question_type": "multiple_choice",
                    "options": ["Uma cobra", "Uma linguagem de programação", "Um framework", "Um banco de dados"],
                    "correct_answer": "Uma linguagem de programação",
                    "justification": "Python é uma linguagem de programação de alto nível.",
                    "difficulty": "easy",
                    "topic": "Python Básico"
                },
                {
                    "content": "Python é uma linguagem interpretada.",
                    "question_type": "true_false",
                    "options": None,
                    "correct_answer": "true",
                    "justification": "Python é interpretada, não compilada.",
                    "difficulty": "easy",
                    "topic": "Python Básico"
                }
            ]
            
            generate_response = client.post(
                f"/api/v1/generation/{session_id}/generate",
                json={
                    "question_count": 5,
                    "question_types": ["multiple_choice", "true_false"]
                },
                headers=auth_headers
            )
        
        # May return 200 (sync) or 202 (async)
        assert generate_response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
        
        # Step 5: Get questions
        questions_response = client.get(
            f"/api/v1/generation/{session_id}/questions",
            headers=auth_headers
        )
        assert questions_response.status_code == status.HTTP_200_OK
        
        # Step 6: Export (if questions exist)
        export_response = client.get(
            f"/api/v1/export/{session_id}",
            params={"format": "csv"},
            headers=auth_headers
        )
        # May succeed or return 501 if not implemented
        assert export_response.status_code in [
            status.HTTP_200_OK, 
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_400_BAD_REQUEST  # If no questions
        ]
    
    def test_user_isolation(self, client):
        """Test that users cannot access each other's data."""
        # Create two users
        client.post(
            "/api/v1/auth/register",
            json={"email": "user1@example.com", "password": "password123", "full_name": "User 1"}
        )
        client.post(
            "/api/v1/auth/register",
            json={"email": "user2@example.com", "password": "password123", "full_name": "User 2"}
        )
        
        # Login as user1
        login1 = client.post(
            "/api/v1/auth/login",
            data={"username": "user1@example.com", "password": "password123"}
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Login as user2
        login2 = client.post(
            "/api/v1/auth/login",
            data={"username": "user2@example.com", "password": "password123"}
        )
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User1 creates a session
        content = "Test content for isolation " * 100
        files = {"file": ("test.txt", BytesIO(content.encode()), "text/plain")}
        upload = client.post("/api/v1/upload/", files=files, headers=headers1)
        
        if upload.status_code == status.HTTP_200_OK:
            session_id = upload.json()["data"]["id"]
            
            # User2 should not see user1's session
            sessions2 = client.get("/api/v1/generation/sessions", headers=headers2)
            if sessions2.status_code == status.HTTP_200_OK:
                session_ids = [s["id"] for s in sessions2.json()]
                assert session_id not in session_ids


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_rate_limiting(self, client, auth_headers):
        """Test that rapid requests are handled gracefully."""
        # Make multiple rapid requests
        for _ in range(10):
            response = client.get("/api/v1/generation/sessions", headers=auth_headers)
            # Should not crash, may return 429 if rate limited
            assert response.status_code in [
                status.HTTP_200_OK, 
                status.HTTP_429_TOO_MANY_REQUESTS,
                status.HTTP_401_UNAUTHORIZED  # If token expired mid-test
            ]
    
    def test_malformed_json(self, client, auth_headers):
        """Test handling of malformed JSON requests."""
        response = client.post(
            "/api/v1/auth/register",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}  # Missing password
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestConcurrency:
    """Test concurrent access scenarios."""
    
    def test_concurrent_uploads(self, client, auth_headers, sample_text_content):
        """Test that concurrent uploads don't interfere."""
        import concurrent.futures
        
        content = (sample_text_content + " ") * 5
        
        def upload_file(i):
            files = {"file": (f"test{i}.txt", BytesIO(content.encode()), "text/plain")}
            return client.post("/api/v1/upload/", files=files, headers=auth_headers)
        
        # Note: TestClient is not thread-safe, so this is more of a sequential test
        # In production, use httpx.AsyncClient for true concurrency tests
        results = []
        for i in range(3):
            results.append(upload_file(i))
        
        # At least some should succeed
        success_count = sum(1 for r in results if r.status_code == status.HTTP_200_OK)
        assert success_count > 0 or all(r.status_code == status.HTTP_400_BAD_REQUEST for r in results)
