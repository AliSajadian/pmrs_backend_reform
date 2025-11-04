"""
Accounts config for the accounts application.
"""
from django.apps import AppConfig


class AccountConfig(AppConfig):
    """
    Account config for the accounts application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = "Access Level"