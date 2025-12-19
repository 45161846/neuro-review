import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String, Text, Integer, Boolean, text
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./ai_reviewer.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PullRequest(BaseModel):
    __tablename__ = "pull_requests"

    pr_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    repository: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(512))
    author: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(50), default="open")
    diff_url: Mapped[str] = mapped_column(String(500))
    base_commit: Mapped[str] = mapped_column(String(100))
    head_commit: Mapped[str] = mapped_column(String(100))
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)


class Review(BaseModel):
    __tablename__ = "reviews"

    pr_id: Mapped[int] = mapped_column(Integer, index=True)
    review_text: Mapped[str] = mapped_column(Text)
    critical_issues: Mapped[int] = mapped_column(Integer, default=0)
    suggestions: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)