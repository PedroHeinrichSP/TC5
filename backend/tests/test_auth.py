"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestAuthRegister:
    """Test user registration endpoint."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # Same as test_user
                "password": "anotherpassword",
                "full_name": "Duplicate User"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já existe" in response.json()["detail"].lower() or "already" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "full_name": "Invalid Email User"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client):
        """Test registration with short password fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@example.com",
                "password": "123",
                "full_name": "Short Pass User"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, test_user):
        """Test successful login returns token."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nobody@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthMe:
    """Test current user endpoint."""
    
    def test_get_current_user(self, client, test_user, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth fails."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token fails."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
