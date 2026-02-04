import os
from celery import Celery
import config
from indexare_incrementala import indexare_incrementala
from celery.schedules import crontab

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery("pypro_search", broker=BROKER_URL, backend=BACKEND_URL)
celery_app.conf.beat_schedule = {
    'indexare-automata-la-fiecare-ora': {
        'task': 'pypro.indexare_incrementala',
        'schedule': crontab(minute=0),
    },
}

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=int(os.getenv("CELERY_PREFETCH_MULTIPLIER", "1")),
)

@celery_app.task(name="pypro.indexare_incrementala", bind=True)
def run_indexare_incrementala(self, folder_path=None):
    target_folder = folder_path or os.getenv("INDEXING_FOLDER", config.DEFAULT_INDEXING_FOLDER)
    print(f"Celery task start indexing folder: {target_folder}")
    try:
        indexare_incrementala(target_folder)
    except Exception as exc:
        print(f"Celery task failed: {exc}")
        raise
    print("Celery task completed")
    return {"folder": target_folder}
