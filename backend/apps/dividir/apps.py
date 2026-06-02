# backend/apps/dividir/apps.py
from django.apps import AppConfig

class DividirConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dividir'

    def ready(self):
        import apps.dividir.signals  # <-- Esto activa las señales