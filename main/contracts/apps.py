"""
Contracts config for the contracts application.
"""
from django.apps import AppConfig


class ContractConfig(AppConfig):
    """
    Contract config for the contracts application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contracts'
    verbose_name = "Contracts Info"