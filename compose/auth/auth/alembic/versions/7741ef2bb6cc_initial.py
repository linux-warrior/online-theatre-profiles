"""initial

Revision ID: 7741ef2bb6cc
Revises: 
Create Date: 2025-02-08 18:12:09.269520

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7741ef2bb6cc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA auth')
    op.create_table(
        'role',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('code', sa.TEXT(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_role')),
        sa.UniqueConstraint('code', name=op.f('uq_role_code')),
        schema='auth',
    )
    op.create_table(
        'user',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('login', sa.TEXT(), nullable=True),
        sa.Column('password', sa.TEXT(), nullable=True),
        sa.Column('email', sa.TEXT(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_email'),
        'user',
        ['email'],
        unique=True,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_login'),
        'user',
        ['login'],
        unique=True,
        schema='auth',
    )
    op.create_table(
        'login_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('user_agent', sa.TEXT(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['auth.user.id'],
            name=op.f('fk_login_history_user_id_user'),
        ),
        sa.PrimaryKeyConstraint('id', 'created', name=op.f('pk_login_history')),
        schema='auth',
        postgresql_partition_by='RANGE (created)',
    )
    op.create_index(
        'ix_login_history_user_id_created',
        'login_history',
        ['user_id', 'created'],
        unique=False,
        schema='auth',
    )
    op.create_table(
        'oauth_account',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('oauth_name', sa.TEXT(), nullable=False),
        sa.Column('access_token', sa.TEXT(), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('refresh_token', sa.TEXT(), nullable=True),
        sa.Column('account_id', sa.TEXT(), nullable=False),
        sa.Column('account_email', sa.TEXT(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['auth.user.id'],
            name=op.f('fk_oauth_account_user_id_user'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_oauth_account')),
        sa.UniqueConstraint('oauth_name', 'account_id', name=op.f('uq_oauth_account_oauth_name')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_oauth_account_account_id'),
        'oauth_account',
        ['account_id'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_oauth_account_oauth_name'),
        'oauth_account',
        ['oauth_name'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_oauth_account_user_id'),
        'oauth_account',
        ['user_id'],
        unique=False,
        schema='auth',
    )
    op.create_table(
        'user_role',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role_id', sa.UUID(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['role_id'],
            ['auth.role.id'],
            name=op.f('fk_user_role_role_id_role'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['auth.user.id'],
            name=op.f('fk_user_role_user_id_user'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_role')),
        sa.UniqueConstraint('user_id', 'role_id', name=op.f('uq_user_role_user_id')),
        schema='auth',
    )


def downgrade() -> None:
    op.drop_table('user_role', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_user_id'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_oauth_name'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_account_id'), table_name='oauth_account', schema='auth')
    op.drop_table('oauth_account', schema='auth')
    op.drop_index('ix_login_history_user_id_created', table_name='login_history', schema='auth')
    op.drop_table('login_history', schema='auth')
    op.drop_index(op.f('ix_auth_user_login'), table_name='user', schema='auth')
    op.drop_index(op.f('ix_auth_user_email'), table_name='user', schema='auth')
    op.drop_table('user', schema='auth')
    op.drop_table('role', schema='auth')
    op.execute('DROP SCHEMA auth')
