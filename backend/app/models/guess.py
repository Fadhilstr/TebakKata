from sqlalchemy import Column, BigInteger, String, Float, Integer, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class Guess(Base):
    __tablename__ = "guesses"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("daily_games.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    word_id = Column(BigInteger, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    ranking = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    game = relationship("DailyGame", back_populates="guesses")
    word = relationship("Word", foreign_keys=[word_id])

    def __repr__(self):
        return f"<Guess(game_id={self.game_id}, word_id={self.word_id}, rank=#{self.ranking})>"
