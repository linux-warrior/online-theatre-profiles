# Generated by Django 5.2.2 on 2025-06-12 19:50
from __future__ import annotations

from collections.abc import Sequence

from django.db import migrations, models
from django.db.migrations.operations.base import Operation

import profiles_admin.models


class Migration(migrations.Migration):
    initial = True

    dependencies: Sequence[tuple[str, str]] = [
    ]

    operations: Sequence[Operation] = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', profiles_admin.models.UUIDPrimaryKey(serialize=False)),
                ('film_id', models.UUIDField(verbose_name='film ID')),
                ('created', profiles_admin.models.CreationField(verbose_name='created')),
            ],
            options={
                'verbose_name': 'user favorite',
                'verbose_name_plural': 'user favorites',
                'db_table': '"profiles"."favorite"',
                'managed': False,
            },
        ),

        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', profiles_admin.models.UUIDPrimaryKey(serialize=False)),
                ('user_id', models.UUIDField(unique=True, verbose_name='user ID')),
                ('last_name', models.TextField(verbose_name='last name')),
                ('first_name', models.TextField(verbose_name='first name')),
                ('patronymic', models.TextField(verbose_name='patronymic')),
                ('phone_number', models.TextField(null=True, unique=True, verbose_name='phone number')),
                ('phone_number_hash', models.TextField(null=True, unique=True, verbose_name='phone number hash')),
                ('created', profiles_admin.models.CreationField(verbose_name='created')),
                ('modified', profiles_admin.models.ModificationField(verbose_name='modified')),
            ],
            options={
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profiles',
                'db_table': '"profiles"."profile"',
                'managed': False,
            },
        ),

        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', profiles_admin.models.UUIDPrimaryKey(serialize=False)),
                ('film_id', models.UUIDField(verbose_name='film ID')),
                ('rating', models.DecimalField(decimal_places=1, max_digits=3, verbose_name='rating')),
                ('created', profiles_admin.models.CreationField(verbose_name='created')),
                ('modified', profiles_admin.models.ModificationField(verbose_name='modified')),
            ],
            options={
                'verbose_name': 'user rating',
                'verbose_name_plural': 'user ratings',
                'db_table': '"profiles"."rating"',
                'managed': False,
            },
        ),

        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', profiles_admin.models.UUIDPrimaryKey(serialize=False)),
                ('film_id', models.UUIDField(verbose_name='film ID')),
                ('summary', models.TextField(verbose_name='summary')),
                ('content', models.TextField(verbose_name='content')),
                ('rating', models.DecimalField(decimal_places=1, max_digits=3, null=True, verbose_name='rating')),
                ('created', profiles_admin.models.CreationField(verbose_name='created')),
                ('modified', profiles_admin.models.ModificationField(verbose_name='modified')),
            ],
            options={
                'verbose_name': 'user review',
                'verbose_name_plural': 'user reviews',
                'db_table': '"profiles"."review"',
                'managed': False,
            },
        ),
    ]
