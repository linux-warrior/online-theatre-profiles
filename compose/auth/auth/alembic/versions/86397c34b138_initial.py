"""initial

Revision ID: 86397c34b138
Revises:
Create Date: 2025-05-31 10:39:32.174356

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '86397c34b138'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA auth')

    op.create_table(
        'permission',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('code', sa.TEXT(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_permission')),
        sa.UniqueConstraint('name', name=op.f('uq_permission_name')),
        sa.UniqueConstraint('code', name=op.f('uq_permission_code')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_permission_created'),
        'permission',
        ['created'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_permission_modified'),
        'permission',
        ['modified'],
        unique=False,
        schema='auth',
    )

    op.create_table(
        'role',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.TEXT(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_role')),
        sa.UniqueConstraint('name', name=op.f('uq_role_name')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_role_created'),
        'role',
        ['created'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_role_modified'),
        'role',
        ['modified'],
        unique=False,
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
        sa.UniqueConstraint('login', name=op.f('uq_user_login')),
        sa.UniqueConstraint('email', name=op.f('uq_user_email')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_created'),
        'user',
        ['created'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_modified'),
        'user',
        ['modified'],
        unique=False,
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
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_login_history')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_login_history_created'),
        'login_history',
        ['created'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_login_history_user_id'),
        'login_history',
        ['user_id'],
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
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
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
        op.f('ix_auth_oauth_account_created'),
        'oauth_account',
        ['created'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_oauth_account_modified'),
        'oauth_account',
        ['modified'],
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
        'role_permission',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('role_id', sa.UUID(), nullable=False),
        sa.Column('permission_id', sa.UUID(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['permission_id'],
            ['auth.permission.id'],
            name=op.f('fk_role_permission_permission_id_permission'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['role_id'],
            ['auth.role.id'],
            name=op.f('fk_role_permission_role_id_role'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_role_permission')),
        sa.UniqueConstraint('role_id', 'permission_id', name=op.f('uq_role_permission_role_id')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_role_permission_created'),
        'role_permission',
        ['created'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_role_permission_permission_id'),
        'role_permission',
        ['permission_id'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_role_permission_role_id'),
        'role_permission',
        ['role_id'],
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
    op.create_index(
        op.f('ix_auth_user_role_created'),
        'user_role',
        ['created'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_role_role_id'),
        'user_role',
        ['role_id'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_role_user_id'),
        'user_role',
        ['user_id'],
        unique=False,
        schema='auth',
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_auth_user_role_user_id'), table_name='user_role', schema='auth')
    op.drop_index(op.f('ix_auth_user_role_role_id'), table_name='user_role', schema='auth')
    op.drop_index(op.f('ix_auth_user_role_created'), table_name='user_role', schema='auth')
    op.drop_table('user_role', schema='auth')

    op.drop_index(op.f('ix_auth_role_permission_role_id'), table_name='role_permission', schema='auth')
    op.drop_index(op.f('ix_auth_role_permission_permission_id'), table_name='role_permission', schema='auth')
    op.drop_index(op.f('ix_auth_role_permission_created'), table_name='role_permission', schema='auth')
    op.drop_table('role_permission', schema='auth')

    op.drop_index(op.f('ix_auth_oauth_account_user_id'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_oauth_name'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_modified'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_created'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_account_id'), table_name='oauth_account', schema='auth')
    op.drop_table('oauth_account', schema='auth')

    op.drop_index(op.f('ix_auth_login_history_user_id'), table_name='login_history', schema='auth')
    op.drop_index(op.f('ix_auth_login_history_created'), table_name='login_history', schema='auth')
    op.drop_table('login_history', schema='auth')

    op.drop_index(op.f('ix_auth_user_modified'), table_name='user', schema='auth')
    op.drop_index(op.f('ix_auth_user_created'), table_name='user', schema='auth')
    op.drop_table('user', schema='auth')

    op.drop_index(op.f('ix_auth_role_modified'), table_name='role', schema='auth')
    op.drop_index(op.f('ix_auth_role_created'), table_name='role', schema='auth')
    op.drop_table('role', schema='auth')

    op.drop_index(op.f('ix_auth_permission_modified'), table_name='permission', schema='auth')
    op.drop_index(op.f('ix_auth_permission_created'), table_name='permission', schema='auth')
    op.drop_table('permission', schema='auth')

    op.execute('DROP SCHEMA auth')
