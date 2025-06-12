from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProfilesAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles_admin'
    verbose_name = _('Profiles service')
