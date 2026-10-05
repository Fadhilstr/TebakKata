import uuid
from sqlalchemy import Column, Date, BigInteger, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class DailyGame(Base):
    __tablename__ = "daily_games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    game_date = Column(Date, unique=True, index=True, nullable=False)
    secret_word_id = Column(BigInteger, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    secret_word = relationship("Word", foreign_keys=[secret_word_id])
    guesses = relationship("Guess", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DailyGame(date={self.game_date}, id={self.id})>"
