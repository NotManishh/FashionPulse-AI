"""Initial schema for FashionPulse AI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-28 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. collected_content
    op.create_table(
        'collected_content',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('platform', sa.String(length=32), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('author_id', sa.String(length=128), nullable=True),
        sa.Column('permalink', sa.String(length=1024), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('raw_metrics', sa.JSON(), nullable=True),
        sa.Column('normalized_engagement', sa.Float(), nullable=True),
        sa.Column('is_fashion_related', sa.Boolean(), nullable=True),
        sa.Column('fashion_confidence', sa.Float(), nullable=True),
        sa.Column('extracted_terms', sa.JSON(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('platform', 'external_id', name='uq_platform_external_id')
    )
    op.create_index('ix_collected_content_platform', 'collected_content', ['platform'], unique=False)
    op.create_index('ix_collected_content_published_at', 'collected_content', ['published_at'], unique=False)
    op.create_index('ix_content_platform_pubdate', 'collected_content', ['platform', 'published_at'], unique=False)

    # 2. trends
    op.create_table(
        'trends',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('current_rank', sa.Integer(), nullable=True),
        sa.Column('current_score', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('momentum_score', sa.Float(), nullable=True),
        sa.Column('growth_rate', sa.Float(), nullable=True),
        sa.Column('growth_status', sa.String(length=32), nullable=True),
        sa.Column('mention_count', sa.Integer(), nullable=True),
        sa.Column('total_engagement', sa.Float(), nullable=True),
        sa.Column('platform_breakdown', sa.JSON(), nullable=True),
        sa.Column('first_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_window', sa.String(length=16), nullable=True),
        sa.Column('supporting_keywords', sa.JSON(), nullable=True),
        sa.Column('representative_references', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_trends_current_rank', 'trends', ['current_rank'], unique=False)
    op.create_index('ix_trends_current_score', 'trends', ['current_score'], unique=False)

    # 3. trend_observations
    op.create_table(
        'trend_observations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trend_id', sa.String(length=36), nullable=False),
        sa.Column('observation_window_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('observation_window_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('mention_count', sa.Integer(), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('trend_score', sa.Float(), nullable=True),
        sa.Column('platform', sa.String(length=32), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['trend_id'], ['trends.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trend_observations_trend_id', 'trend_observations', ['trend_id'], unique=False)

    # 4. collection_jobs
    op.create_table(
        'collection_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('platform', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('records_collected', sa.Integer(), nullable=True),
        sa.Column('records_new', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trigger_type', sa.String(length=32), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. connector_statuses
    op.create_table(
        'connector_statuses',
        sa.Column('platform', sa.String(length=32), nullable=False),
        sa.Column('is_configured', sa.Boolean(), nullable=True),
        sa.Column('is_authorized', sa.Boolean(), nullable=True),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.Column('total_records_ingested', sa.Integer(), nullable=True),
        sa.Column('rate_limit_info', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('platform')
    )

    # 6. nemotron_handoffs
    op.create_table(
        'nemotron_handoffs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('response_status_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('nemotron_handoffs')
    op.drop_table('connector_statuses')
    op.drop_table('collection_jobs')
    op.drop_table('trend_observations')
    op.drop_table('trends')
    op.drop_table('collected_content')
