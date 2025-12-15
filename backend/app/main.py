"""
Gerador de Questões Acadêmicas com IA
Aplicação principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import auth, upload, generation, export

# Configura logging estruturado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicacao"""
    # Startup
    logger.info("application_starting", app_name=settings.app_name)
    
    # Log da URL do banco (sem senha)
    db_url = settings.database_url
    if "@" in db_url:
        # Oculta a senha no log
        safe_url = db_url.split("@")[0].rsplit(":", 1)[0] + ":***@" + db_url.split("@")[1]
    else:
        safe_url = db_url
    logger.info("database_connecting", url=safe_url)
    
    # Cria tabelas do banco de dados
    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_created")
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")


# Cria aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    description="""
    ## Sistema Gerador de Questões Acadêmicas com IA
    
    API para geração automática de questões a partir de documentos acadêmicos.
    
    ### Funcionalidades:
    - Upload de arquivos PDF, DOCX, TXT
    - Geração de questões de múltipla escolha, V/F e dissertativas
    - Classificação automática de dificuldade
    - Edição e revisão de questões
    - Exportação em PDF, CSV e TXT
    
    ### Tecnologias:
    - FastAPI + PostgreSQL
    - OpenAI / Gemini / Claude
    - NLP com TF-IDF e K-Means
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Inclui rotas
app.include_router(auth.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(generation.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Endpoint raiz - health check"""
    return {
        "status": "online",
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check detalhado"""
    from app.services.ai.base import AIProviderFactory
    
    available_providers = AIProviderFactory.get_available_providers()
    
    return {
        "status": "healthy",
        "database": "connected",
        "ai_providers": {
            "available": available_providers,
            "default": settings.ai_provider
        },
        "config": {
            "max_questions": settings.max_questions_per_request,
            "max_file_size_mb": settings.max_file_size_mb,
            "allowed_formats": settings.allowed_extensions_list
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
