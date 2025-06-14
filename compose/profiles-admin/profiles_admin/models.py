from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDPrimaryKey(models.UUIDField):
    def __init__(self, **kwargs: Any) -> None:
        kwargs.update({
            'primary_key': True,
            'default': uuid.uuid4,
            'editable': False,
        })
        super().__init__(**kwargs)

    def deconstruct(self) -> tuple[str, str, Sequence, dict]:
        name, path, args, kwargs = super().deconstruct()

        for kwarg_name in ('primary_key', 'default', 'editable'):
            del kwargs[kwarg_name]

        return name, path, args, kwargs


class CreationField(models.DateTimeField):
    def __init__(self, **kwargs: Any) -> None:
        kwargs = {
            'verbose_name': _('created'),
            **kwargs,
            'auto_now_add': True,
        }
        super().__init__(**kwargs)

    def deconstruct(self) -> tuple[str, str, Sequence, dict]:
        name, path, args, kwargs = super().deconstruct()

        del kwargs['auto_now_add']

        return name, path, args, kwargs


class ModificationField(models.DateTimeField):
    def __init__(self, **kwargs: Any) -> None:
        kwargs = {
            'verbose_name': _('modified'),
            **kwargs,
            'auto_now': True,
        }
        super().__init__(**kwargs)

    def deconstruct(self) -> tuple[str, str, Sequence, dict]:
        name, path, args, kwargs = super().deconstruct()

        del kwargs['auto_now']

        return name, path, args, kwargs


class Profile(models.Model):
    id = UUIDPrimaryKey()
    user_id = models.UUIDField(
        verbose_name=_('user ID'),
        unique=True,
    )
    last_name = models.TextField(
        verbose_name=_('last name'),
    )
    first_name = models.TextField(
        verbose_name=_('first name'),
    )
    patronymic = models.TextField(
        verbose_name=_('patronymic'),
    )
    phone_number = models.TextField(
        verbose_name=_('phone number'),
        unique=True,
        null=True,
    )
    phone_number_hash = models.TextField(
        verbose_name=_('phone number hash'),
        unique=True,
        null=True,
    )
    created = CreationField()
    modified = ModificationField()

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        managed = False
        db_table = '"profiles"."profile"'


class Favorite(models.Model):
    id = UUIDPrimaryKey()
    profile = models.ForeignKey(
        verbose_name=_('user profile'),
        to='Profile',
        on_delete=models.DO_NOTHING,
    )
    film_id = models.UUIDField(
        verbose_name=_('film ID'),
    )
    created = CreationField()

    class Meta:
        verbose_name = _('user favorite')
        verbose_name_plural = _('user favorites')
        managed = False
        db_table = '"profiles"."favorite"'
        unique_together = ['profile', 'film_id']


class Rating(models.Model):
    id = UUIDPrimaryKey()
    profile = models.ForeignKey(
        verbose_name=_('user profile'),
        to='Profile',
        on_delete=models.DO_NOTHING,
    )
    film_id = models.UUIDField(
        verbose_name=_('film ID'),
    )
    rating = models.DecimalField(
        verbose_name=_('rating'),
        max_digits=3,
        decimal_places=1,
    )
    created = CreationField()
    modified = ModificationField()

    class Meta:
        verbose_name = _('user rating')
        verbose_name_plural = _('user ratings')
        managed = False
        db_table = '"profiles"."rating"'
        unique_together = ['profile', 'film_id']


class Review(models.Model):
    id = UUIDPrimaryKey()
    profile = models.ForeignKey(
        verbose_name=_('user profile'),
        to='Profile',
        on_delete=models.DO_NOTHING,
    )
    film_id = models.UUIDField(
        verbose_name=_('film ID'),
    )
    summary = models.TextField(
        verbose_name=_('summary'),
    )
    content = models.TextField(
        verbose_name=_('content'),
    )
    rating = models.DecimalField(
        verbose_name=_('rating'),
        null=True,
        max_digits=3,
        decimal_places=1,
    )
    created = CreationField()
    modified = ModificationField()

    class Meta:
        verbose_name = _('user review')
        verbose_name_plural = _('user reviews')
        managed = False
        db_table = '"profiles"."review"'
        unique_together = ['profile', 'film_id']
