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
    Index,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
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
    login: Mapped[str] = mapped_column(TEXT, unique=True, index=True, nullable=True)
    password: Mapped[str] = mapped_column(TEXT, nullable=True)
    email: Mapped[str] = mapped_column(TEXT, unique=True, index=True, nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    roles: Mapped[list[UserRole]] = relationship(
        "UserRole", cascade="all, delete", back_populates="user"
    )
    login_history: Mapped[list[LoginHistory]] = relationship(
        "LoginHistory", cascade="all, delete-orphan", back_populates="user"
    )
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        'OAuthAccount',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='joined',
    )


class Role(AuthBase):
    __tablename__ = 'role'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(TEXT)
    code: Mapped[str] = mapped_column(TEXT, unique=True)
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
        "UserRole", cascade="all, delete", back_populates="role"
    )


class UserRole(AuthBase):
    __tablename__ = 'user_role'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('auth.user.id', ondelete='CASCADE'))
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('auth.role.id', ondelete='CASCADE'))
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
        "User", back_populates="roles"
    )
    role: Mapped[Role] = relationship(
        "Role", back_populates="user_roles"
    )


class LoginHistory(AuthBase):
    __tablename__ = 'login_history'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('auth.user.id'))
    user_agent: Mapped[str] = mapped_column(TEXT)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        primary_key=True
    )

    __table_args__ = (
        Index('ix_login_history_user_id_created', 'user_id', 'created'),
        {
            'postgresql_partition_by': 'RANGE (created)',
        }
    )

    user: Mapped[User] = relationship(
        "User", cascade='all, delete', back_populates="login_history"
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
    oauth_name: Mapped[str] = mapped_column(TEXT, index=True)
    access_token: Mapped[str] = mapped_column(TEXT)
    expires_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    account_id: Mapped[str] = mapped_column(TEXT, index=True)
    account_email: Mapped[str] = mapped_column(TEXT)

    user: Mapped[User] = relationship('User', back_populates='oauth_accounts')

    __table_args__ = (
        UniqueConstraint('oauth_name', 'account_id'),
    )
