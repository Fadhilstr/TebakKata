from sqlalchemy import Column, BigInteger, String, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class WordRelation(Base):
    __tablename__ = "word_relations"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    word_id = Column(BigInteger, ForeignKey("words.id", ondelete="CASCADE"), nullable=False, index=True)
    related_word_id = Column(BigInteger, ForeignKey("words.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(50), nullable=False)  # synonym, hypernym, contextual, etc.
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    word = relationship("Word", foreign_keys=[word_id])
    related_word = relationship("Word", foreign_keys=[related_word_id])

    def __repr__(self):
        return f"<WordRelation({self.word_id} -> {self.related_word_id}, type='{self.relation_type}')>"
