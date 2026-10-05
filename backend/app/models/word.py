from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, func
from pgvector.sqlalchemy import Vector
from app.db.session import Base
from app.core.config import settings


class Word(Base):
    __tablename__ = "words"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    word = Column(String(100), nullable=False)
    normalized_word = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=True, default=None)
    frequency = Column(Integer, nullable=False, default=0)
    is_secret_eligible = Column(Boolean, nullable=False, default=False, index=True)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Word(id={self.id}, word='{self.word}')>"
