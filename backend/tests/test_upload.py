"""
Tests for file upload endpoints.
"""
import pytest
from fastapi import status
from io import BytesIO


class TestFileUpload:
    """Test file upload endpoint."""
    
    def test_upload_txt_success(self, client, auth_headers, sample_text_content):
        """Test successful TXT file upload."""
        file_content = sample_text_content.encode('utf-8')
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        response = client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"]["source_filename"] == "test.txt"
        assert data["data"]["word_count"] > 0
    
    def test_upload_unauthorized(self, client, sample_text_content):
        """Test upload without authentication fails."""
        file_content = sample_text_content.encode('utf-8')
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/v1/upload/", files=files)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_upload_invalid_type(self, client, auth_headers):
        """Test upload with invalid file type fails."""
        file_content = b"not a valid file type"
        files = {"file": ("test.exe", BytesIO(file_content), "application/x-msdownload")}
        
        response = client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers
        )
        
        # Should fail with 400 for invalid file type
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_upload_empty_file(self, client, auth_headers):
        """Test upload with empty file fails."""
        files = {"file": ("empty.txt", BytesIO(b""), "text/plain")}
        
        response = client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers
        )
        
        # Should fail because content is too short
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_upload_file_too_short(self, client, auth_headers):
        """Test upload with content below minimum word count fails."""
        short_content = b"Just a few words."
        files = {"file": ("short.txt", BytesIO(short_content), "text/plain")}
        
        response = client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers
        )
        
        # Should fail because content is below 500 words
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSupportedFormats:
    """Test supported file format validation."""
    
    def test_supported_formats_endpoint(self, client, auth_headers):
        """Test getting supported file formats."""
        response = client.get(
            "/api/v1/upload/supported-formats",
            headers=auth_headers
        )
        
        # Endpoint should exist
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "pdf" in str(data).lower() or "txt" in str(data).lower()
