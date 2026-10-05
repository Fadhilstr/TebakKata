"""Initial tables with pgvector

Revision ID: 001_initial_tables
Revises: 
Create Date: 2026-10-05 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import pgvector.sqlalchemy

revision: str = '001_initial_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Table: words
    op.create_table(
        'words',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('word', sa.String(length=100), nullable=False),
        sa.Column('normalized_word', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('frequency', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_secret_eligible', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_words_id', 'words', ['id'], unique=False)
    op.create_index('ix_words_normalized_word', 'words', ['normalized_word'], unique=True)
    op.create_index('ix_words_is_secret_eligible', 'words', ['is_secret_eligible'], unique=False)

    # 3. Table: daily_games
    op.create_table(
        'daily_games',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('game_date', sa.Date(), nullable=False),
        sa.Column('secret_word_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['secret_word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_daily_games_id', 'daily_games', ['id'], unique=False)
    op.create_index('ix_daily_games_game_date', 'daily_games', ['game_date'], unique=True)

    # 4. Table: guesses
    op.create_table(
        'guesses',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('game_id', UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('word_id', sa.BigInteger(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('ranking', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['daily_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_guesses_id', 'guesses', ['id'], unique=False)
    op.create_index('ix_guesses_game_session', 'guesses', ['game_id', 'session_id'], unique=False)
    op.create_index('ix_guesses_ranking', 'guesses', ['ranking'], unique=False)

    # 5. Table: word_relations
    op.create_table(
        'word_relations',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('word_id', sa.BigInteger(), nullable=False),
        sa.Column('related_word_id', sa.BigInteger(), nullable=False),
        sa.Column('relation_type', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_word_relations_word_id', 'word_relations', ['word_id'], unique=False)
    op.create_index('ix_word_relations_related_word_id', 'word_relations', ['related_word_id'], unique=False)


def downgrade() -> None:
    op.drop_table('word_relations')
    op.drop_table('guesses')
    op.drop_table('daily_games')
    op.drop_table('words')
