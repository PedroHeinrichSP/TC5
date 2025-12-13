"""
Pytest configuration and fixtures for testing.
"""
import os
import sys
import pytest
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock, patch

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.models import User


# Test database setup - using SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Create a test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Create authentication headers for test user."""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider for testing question generation."""
    mock = MagicMock()
    mock.generate_questions = AsyncMock(return_value=[
        {
            "content": "Qual é a capital do Brasil?",
            "question_type": "multiple_choice",
            "options": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador"],
            "correct_answer": "Brasília",
            "justification": "Brasília é a capital federal do Brasil desde 1960.",
            "difficulty": "easy",
            "topic": "Geografia"
        },
        {
            "content": "O Python é uma linguagem compilada.",
            "question_type": "true_false",
            "options": None,
            "correct_answer": "false",
            "justification": "Python é uma linguagem interpretada, não compilada.",
            "difficulty": "medium",
            "topic": "Programação"
        }
    ])
    return mock


@pytest.fixture
def sample_text_content() -> str:
    """Sample text content for testing."""
    return """
    Python é uma linguagem de programação de alto nível, interpretada e de propósito geral.
    Foi criada por Guido van Rossum e lançada em 1991. Python possui tipagem dinâmica e
    gerenciamento automático de memória. Suporta múltiplos paradigmas de programação,
    incluindo programação estruturada, orientada a objetos e funcional.
    
    As principais características do Python incluem:
    - Sintaxe clara e legível
    - Grande biblioteca padrão
    - Suporte a múltiplos paradigmas
    - Interpretado (não compilado)
    - Tipagem dinâmica
    
    O Python é amplamente utilizado em desenvolvimento web, ciência de dados, 
    inteligência artificial, automação e muitas outras áreas.
    """


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generate a minimal valid PDF for testing."""
    # Minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF"""
    return pdf_content
