from celery import Celery, group, chain
from celery.schedules import crontab
from config.settings import settings
import logging

tickers = ["chmf", "ugld", "vtbr", "nlmk", "magn"]

emitents = {
    "chmf": 255,
    "ugld": 9735,
    "vtbr": 50,
    "nlmk": 2529,
    "magn": 33,
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "file_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['src.celery_app'] # Include this module for task discovery
)

celery_app.conf.update(
    task_serializer = 'json',
    accept_content = ["json"],
    result_serializer = "json",
    timezone = "UTC",
    enable_utc = True,
    result_expires = 3600
)

celery_app.conf.beat_schedule = {
    "update-files-every-5-minutes": {
        "task": "src.celery_app.update_files_task",
        "schedule": 300.0, # 5 minutes
        "options": {"max_retries": 3}
    }
    # ,
    # "update-files-every-day": {
    #     "task": "celery_app.update_files_task",
    #     # "schedule": crontab(hour=settings.DAILY_REPORT_HOUR, minute=0),
    #     "schedule": 60*60*24,
    #     "options": {"max_retries": 3}
    # }
}

from tasks.file_update import file_update

@celery_app.task(bind=True, name="src.celery_app.update_files_task")
def update_files_task(self):
    results = []
    try:
        logger.info("Starting scheduled file update task")
        for ticker, emitent_id in emitents.items():
            result = file_update(f"{ticker}", f"{emitent_id}")
            results.append(result)
        return result
    except Exception as e:
        logger.error(f"File update task failed: {str(e)}")
        raise self.retry(countdown=60, max_retries=3, exc=e)