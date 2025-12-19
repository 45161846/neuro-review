from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime

from final_project.src.config import settings
from final_project.src.database import get_db, init_db
from final_project.src.github.webhook import router as webhook_router

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Code Reviewer Bot",
    description="Автоматический ревьюер Pull Request с использованием AI",
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])


@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Code Reviewer Bot...")
    logger.info(f"Environment: {settings.app_env}")

    await init_db()
    logger.info("Database initialized")
    logger.info("GitHub webhook handler ready")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Code Reviewer Bot...")


@app.get("/")
async def root():
    return {
        "service": "AI Code Reviewer Bot for GitHub",
        "status": "running",
        "version": "0.1.0",
        "features": [
            "GitHub PR code review",
            "AI-powered analysis",
            "Markdown comments in PR"
        ]
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Проверка подключения к БД
        result = await db.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.get("/config")
async def get_config():
    """Получение конфигурации (только для отладки)"""
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not available in production"
        )

    return {
        "app_env": settings.app_env,
        "api_port": settings.api_port,
        "postgres_host": settings.postgres_host,
        "database_configured": hasattr(settings, 'database_url') and bool(settings.database_url),
        "github_configured": bool(settings.github_access_token),
        "ai_configured": bool(settings.deepseek_api_key),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
