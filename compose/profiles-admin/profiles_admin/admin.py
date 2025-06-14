from __future__ import annotations

from django.contrib import admin

from .models import (
    Profile,
    Favorite,
    Rating,
    Review,
)


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0

    fields = ()
    readonly_fields = (
        'film_id',
        'created',
    )


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0

    fields = ()
    readonly_fields = (
        'film_id',
        'rating',
        'created',
        'modified',
    )


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0

    fields = ()
    readonly_fields = (
        'film_id',
        'summary',
        'content',
        'rating',
        'created',
        'modified',
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'last_name',
        'first_name',
        'patronymic',
        'created',
        'modified',
    )
    list_filter = (
        'created',
        'modified',
    )

    search_fields = (
        'user_id__iexact',
        'last_name__iexact',
        'first_name__iexact',
        'patronymic__iexact',
    )
    show_full_result_count = False

    fields = ()
    readonly_fields = (
        'id',
        'user_id',
        'last_name',
        'first_name',
        'patronymic',
        'phone_number',
        'phone_number_hash',
        'created',
        'modified',
    )

    inlines = (
        FavoriteInline,
        RatingInline,
        ReviewInline,
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
