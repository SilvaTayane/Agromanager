from django.apps import AppConfig


class MonitoramentoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoramento'

    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()
