"""reviews

Revision ID: 05b7b689bd63
Revises: 0f26da2f9e38
Create Date: 2025-06-06 11:11:22.051719

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '05b7b689bd63'
down_revision: Union[str, None] = '0f26da2f9e38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'review',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('profile_id', sa.UUID(), nullable=False),
        sa.Column('film_id', sa.UUID(), nullable=False),
        sa.Column('summary', sa.TEXT(), nullable=False),
        sa.Column('content', sa.TEXT(), nullable=False),
        sa.Column('rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['profile_id'],
            ['profiles.profile.id'],
            name=op.f('fk_review_profile_id_profile'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_review')),
        sa.UniqueConstraint('profile_id', 'film_id', name=op.f('uq_review_profile_id')),
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_review_created'),
        'review',
        ['created'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_review_film_id'),
        'review',
        ['film_id'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_review_modified'),
        'review',
        ['modified'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_review_profile_id'),
        'review',
        ['profile_id'],
        unique=False,
        schema='profiles',
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_profiles_review_profile_id'), table_name='review', schema='profiles')
    op.drop_index(op.f('ix_profiles_review_modified'), table_name='review', schema='profiles')
    op.drop_index(op.f('ix_profiles_review_film_id'), table_name='review', schema='profiles')
    op.drop_index(op.f('ix_profiles_review_created'), table_name='review', schema='profiles')
    op.drop_table('review', schema='profiles')
