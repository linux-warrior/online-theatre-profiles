"""initial

Revision ID: df903f750dd2
Revises:
Create Date: 2025-06-02 13:32:11.614254

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'df903f750dd2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA profiles')

    op.create_table(
        'profile',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('last_name', sa.TEXT(), nullable=False),
        sa.Column('first_name', sa.TEXT(), nullable=False),
        sa.Column('patronymic', sa.TEXT(), nullable=False),
        sa.Column('phone_number', sa.TEXT(), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('user_id', name=op.f('pk_profile')),
        sa.UniqueConstraint('phone_number', name=op.f('uq_profile_phone_number')),
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_profile_created'),
        'profile',
        ['created'],
        unique=False,
        schema='profiles',
    )
    op.create_index(
        op.f('ix_profiles_profile_modified'),
        'profile',
        ['modified'],
        unique=False,
        schema='profiles',
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_profiles_profile_modified'), table_name='profile', schema='profiles')
    op.drop_index(op.f('ix_profiles_profile_created'), table_name='profile', schema='profiles')
    op.drop_table('profile', schema='profiles')

    op.execute('DROP SCHEMA profiles')
