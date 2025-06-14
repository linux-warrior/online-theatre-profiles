"""empty message

Revision ID: 82154ccf81ea
Revises: 05b7b689bd63
Create Date: 2025-06-13 21:17:45.804958

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '82154ccf81ea'
down_revision: Union[str, None] = '05b7b689bd63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'profile',
        sa.Column('phone_number_hash', sa.TEXT(), nullable=True),
    )
    op.create_unique_constraint(
        op.f('uq_profile_phone_number_hash'),
        'profile',
        ['phone_number_hash'],
        schema='profiles',
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq_profile_phone_number_hash'),
        'profile',
        schema='profiles',
        type_='unique',
    )
    op.drop_column('profile', 'phone_number_hash')
