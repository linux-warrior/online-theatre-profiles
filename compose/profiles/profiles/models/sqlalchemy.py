from __future__ import annotations

import datetime
import decimal
import uuid

from sqlalchemy import (
    MetaData,
    UUID,
    TEXT,
    DateTime,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
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

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        unique=True,
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
    phone_number: Mapped[str | None] = mapped_column(
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

    favorites: Mapped[list[Favorite]] = relationship(
        'Favorite',
        back_populates='profile',
        cascade='all, delete-orphan',
    )
    ratings: Mapped[list[Rating]] = relationship(
        'Rating',
        back_populates='profile',
        cascade='all, delete-orphan',
    )
    reviews: Mapped[list[Review]] = relationship(
        'Review',
        back_populates='profile',
        cascade='all, delete-orphan',
    )


class Favorite(ProfilesBase):
    __tablename__ = 'favorite'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('profiles.profile.id', ondelete='CASCADE'),
        index=True,
    )
    film_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        index=True,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        default=lambda: datetime.datetime.now(datetime.UTC),
    )

    __table_args__ = (
        UniqueConstraint(
            'profile_id',
            'film_id',
        ),
    )

    profile: Mapped[Profile] = relationship(
        'Profile',
        back_populates='favorites',
    )


class Rating(ProfilesBase):
    __tablename__ = 'rating'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('profiles.profile.id', ondelete='CASCADE'),
        index=True,
    )
    film_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        index=True,
    )
    rating: Mapped[decimal.Decimal] = mapped_column(
        Numeric(precision=3, scale=1),
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

    __table_args__ = (
        UniqueConstraint(
            'profile_id',
            'film_id',
        ),
    )

    profile: Mapped[Profile] = relationship(
        'Profile',
        back_populates='ratings',
    )


class Review(ProfilesBase):
    __tablename__ = 'review'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('profiles.profile.id', ondelete='CASCADE'),
        index=True,
    )
    film_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        index=True,
    )
    summary: Mapped[str] = mapped_column(
        TEXT,
    )
    content: Mapped[str] = mapped_column(
        TEXT,
    )
    rating: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(precision=3, scale=1),
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

    __table_args__ = (
        UniqueConstraint(
            'profile_id',
            'film_id',
        ),
    )

    profile: Mapped[Profile] = relationship(
        'Profile',
        back_populates='reviews',
    )
