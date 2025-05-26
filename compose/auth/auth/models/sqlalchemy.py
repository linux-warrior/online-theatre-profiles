from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    MetaData,
    UUID,
    TEXT,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

auth_metadata_obj = MetaData(
    schema='auth',
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    },
)


class AuthBase(DeclarativeBase):
    metadata = auth_metadata_obj


class User(AuthBase):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    login: Mapped[str] = mapped_column(
        TEXT,
        unique=True,
        nullable=True,
    )
    password: Mapped[str] = mapped_column(
        TEXT,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        TEXT,
        unique=True,
        nullable=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    user_roles: Mapped[list[UserRole]] = relationship(
        'UserRole',
        back_populates='user',
        cascade='all, delete-orphan',
    )
    login_history: Mapped[list[LoginHistory]] = relationship(
        'LoginHistory',
        back_populates='user',
        cascade='all, delete-orphan',
    )
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        'OAuthAccount',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class Role(AuthBase):
    __tablename__ = 'role'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        TEXT,
        unique=True,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    user_roles: Mapped[list[UserRole]] = relationship(
        'UserRole',
        back_populates='role',
        cascade='all, delete-orphan',
    )
    role_permissions: Mapped[list[RolePermission]] = relationship(
        'RolePermission',
        back_populates='role',
        cascade='all, delete-orphan',
    )


class UserRole(AuthBase):
    __tablename__ = 'user_role'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('auth.user.id', ondelete='CASCADE'),
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('auth.role.id', ondelete='CASCADE'),
        index=True,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )

    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'role_id',
        ),
    )

    user: Mapped[User] = relationship(
        'User',
        back_populates='user_roles',
    )
    role: Mapped[Role] = relationship(
        'Role',
        back_populates='user_roles',
    )


class Permission(AuthBase):
    __tablename__ = 'permission'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        TEXT,
        unique=True,
    )
    code: Mapped[str] = mapped_column(
        TEXT,
        unique=True,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    role_permissions: Mapped[list[RolePermission]] = relationship(
        'RolePermission',
        back_populates='permission',
        cascade='all, delete-orphan',
    )


class RolePermission(AuthBase):
    __tablename__ = 'role_permission'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('auth.role.id', ondelete='CASCADE'),
        index=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('auth.permission.id', ondelete='CASCADE'),
        index=True,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )

    __table_args__ = (
        UniqueConstraint(
            'role_id',
            'permission_id',
        ),
    )

    role: Mapped[Role] = relationship(
        'Role',
        back_populates='role_permissions',
    )
    permission: Mapped[Permission] = relationship(
        'Permission',
        back_populates='role_permissions',
    )


class LoginHistory(AuthBase):
    __tablename__ = 'login_history'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('auth.user.id', ondelete='CASCADE'),
        index=True,
    )
    user_agent: Mapped[str] = mapped_column(
        TEXT,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )

    user: Mapped[User] = relationship(
        'User',
        back_populates='login_history',
    )


class OAuthAccount(AuthBase):
    __tablename__ = 'oauth_account'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('auth.user.id', ondelete='CASCADE'),
        index=True,
    )
    oauth_name: Mapped[str] = mapped_column(
        TEXT,
        index=True,
    )
    access_token: Mapped[str] = mapped_column(
        TEXT,
    )
    expires_at: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    refresh_token: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )
    account_id: Mapped[str] = mapped_column(
        TEXT,
        index=True,
    )
    account_email: Mapped[str] = mapped_column(
        TEXT,
    )

    __table_args__ = (
        UniqueConstraint('oauth_name', 'account_id'),
    )

    user: Mapped[User] = relationship(
        'User',
        back_populates='oauth_accounts',
    )
