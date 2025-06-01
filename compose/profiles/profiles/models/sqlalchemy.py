from __future__ import annotations

import datetime
import uuid

from sqlalchemy import (
    MetaData,
    UUID,
    TEXT,
    DateTime,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

profiles_metadata_obj = MetaData(
    schema='profiles',
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    },
)


class ProfilesBase(AsyncAttrs, DeclarativeBase):
    metadata = profiles_metadata_obj


class Profile(ProfilesBase):
    __tablename__ = 'profile'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    last_name: Mapped[str] = mapped_column(
        TEXT,
    )
    first_name: Mapped[str] = mapped_column(
        TEXT,
    )
    patronymic: Mapped[str] = mapped_column(
        TEXT,
    )
    phone: Mapped[str | None] = mapped_column(
        TEXT,
        unique=True,
        nullable=True,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
