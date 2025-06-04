"""ratings

Revision ID: 0f26da2f9e38
Revises: b76e44225107
Create Date: 2025-06-04 11:45:39.215300

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0f26da2f9e38'
down_revision: Union[str, None] = 'b76e44225107'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'rating',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('profile_id', sa.UUID(), nullable=False),
        sa.Column('film_id', sa.UUID(), nullable=False),
        sa.Column('rating', sa.Numeric(precision=3, scale=1), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['profile_id'],
            ['profiles.profile.id'],
            name=op.f('fk_rating_profile_id_profile'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_rating')),
        sa.UniqueConstraint('profile_id', 'film_id', name=op.f('uq_rating_profile_id')),
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_rating_created'),
        'rating',
        ['created'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_rating_film_id'),
        'rating',
        ['film_id'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_rating_modified'),
        'rating',
        ['modified'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_rating_profile_id'),
        'rating',
        ['profile_id'],
        unique=False,
        schema='profiles',
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_profiles_rating_profile_id'), table_name='rating', schema='profiles')
    op.drop_index(op.f('ix_profiles_rating_modified'), table_name='rating', schema='profiles')
    op.drop_index(op.f('ix_profiles_rating_film_id'), table_name='rating', schema='profiles')
    op.drop_index(op.f('ix_profiles_rating_created'), table_name='rating', schema='profiles')
    op.drop_table('rating', schema='profiles')
