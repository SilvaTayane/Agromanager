from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from .tasks import coletar_clima

scheduler = None

def start_scheduler():
    global scheduler
    if scheduler is not None:
        return

    scheduler = BackgroundScheduler(timezone=getattr(settings, "TIME_ZONE", None))
    scheduler.add_job(coletar_clima, "interval", hours=6, id="coleta_clima")
    scheduler.start()
    print("Scheduler iniciado: coleta_clima a cada 6 horas")
