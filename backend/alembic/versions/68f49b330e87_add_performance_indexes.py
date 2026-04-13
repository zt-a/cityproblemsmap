"""add_performance_indexes

Revision ID: 68f49b330e87
Revises: df9272d3b653
Create Date: 2026-04-08 12:43:38.498222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68f49b330e87'
down_revision: Union[str, None] = 'df9272d3b653'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Индекс для поиска по геолокации (GIST для PostGIS)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_problems_location_gist
        ON problems USING GIST(location);
    """)

    # Индекс для фильтрации по статусу и дате
    op.create_index(
        'idx_problems_status_created',
        'problems',
        ['status', sa.text('created_at DESC')],
        postgresql_using='btree'
    )

    # Индекс для поиска проблем по зоне и статусу
    op.create_index(
        'idx_problems_zone_status',
        'problems',
        ['zone_entity_id', 'status', 'is_current'],
        postgresql_using='btree'
    )

    # Индекс для поиска комментариев проблемы
    op.create_index(
        'idx_comments_problem_created',
        'comments',
        ['problem_entity_id', sa.text('created_at DESC')],
        postgresql_where=sa.text('is_current = true'),
        postgresql_using='btree'
    )

    # Индекс для подсчета голосов
    op.create_index(
        'idx_votes_problem_user_current',
        'votes',
        ['problem_entity_id', 'user_entity_id', 'is_current'],
        postgresql_using='btree'
    )

    # Индекс для поиска медиа проблемы по категории
    op.create_index(
        'idx_media_problem_category',
        'problem_media',
        ['problem_entity_id', 'media_category', 'is_current'],
        postgresql_using='btree'
    )

    # Индекс для поиска уведомлений пользователя
    op.create_index(
        'idx_notifications_user_read',
        'notifications',
        ['user_entity_id', 'is_read', sa.text('created_at DESC')],
        postgresql_where=sa.text('is_current = true'),
        postgresql_using='btree'
    )

    # Индекс для поиска подписок пользователя
    op.create_index(
        'idx_subscriptions_user_target',
        'subscriptions',
        ['user_entity_id', 'target_type', 'target_entity_id'],
        postgresql_where=sa.text('is_current = true'),
        postgresql_using='btree'
    )

    # Индекс для поиска активности пользователя
    op.create_index(
        'idx_activities_user_created',
        'activities',
        ['user_entity_id', sa.text('created_at DESC')],
        postgresql_where=sa.text('is_current = true'),
        postgresql_using='btree'
    )

    # Индекс для поиска подписчиков
    op.create_index(
        'idx_follows_following_current',
        'follows',
        ['following_entity_id', 'is_current'],
        postgresql_using='btree'
    )


def downgrade() -> None:
    # Удалить индексы в обратном порядке
    op.drop_index('idx_follows_following_current', table_name='follows')
    op.drop_index('idx_activities_user_created', table_name='activities')
    op.drop_index('idx_subscriptions_user_target', table_name='subscriptions')
    op.drop_index('idx_notifications_user_read', table_name='notifications')
    op.drop_index('idx_media_problem_category', table_name='problem_media')
    op.drop_index('idx_votes_problem_user_current', table_name='votes')
    op.drop_index('idx_comments_problem_created', table_name='comments')
    op.drop_index('idx_problems_zone_status', table_name='problems')
    op.drop_index('idx_problems_status_created', table_name='problems')
    op.execute("DROP INDEX IF EXISTS idx_problems_location_gist;")

