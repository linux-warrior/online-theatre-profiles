"""favorites

Revision ID: b76e44225107
Revises: df903f750dd2
Create Date: 2025-06-03 09:55:17.664862

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b76e44225107'
down_revision: Union[str, None] = 'df903f750dd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'favorite',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('profile_id', sa.UUID(), nullable=False),
        sa.Column('film_id', sa.UUID(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['profile_id'],
            ['profiles.profile.id'],
            name=op.f('fk_favorite_profile_id_profile'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_favorite')),
        sa.UniqueConstraint('profile_id', 'film_id', name=op.f('uq_favorite_profile_id')),
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_favorite_created'),
        'favorite',
        ['created'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_favorite_film_id'),
        'favorite',
        ['film_id'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_favorite_profile_id'),
        'favorite',
        ['profile_id'],
        unique=False,
        schema='profiles',
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_profiles_favorite_profile_id'), table_name='favorite', schema='profiles')
    op.drop_index(op.f('ix_profiles_favorite_film_id'), table_name='favorite', schema='profiles')
    op.drop_index(op.f('ix_profiles_favorite_created'), table_name='favorite', schema='profiles')
    op.drop_table('favorite', schema='profiles')
