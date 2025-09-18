from celery import Celery, group, chain
from celery.schedules import crontab
from config.settings import settings
import logging
import asyncio

tickers = ["chmf", "ugld", "vtbr", "nlmk", "magn"]

emitents = {
    "chmf": 255, # severstal
    "ugld": 9735, # южуралзолото
    "vtbr": 50, # втб банк
    "nlmk": 2529, # нлмк
    "magn": 33, # mmk
    "msgn": 126,# мосэнерго
    "mdmg": 577465, # ??????? matiditya OR MD Medical Group Investments
    "ydex": 10705, # yandex
    "alrs": 18, # alrosa
    "aflt": 19, # aeroflot
    "gazp": 21, #gazprom not gazpromneft
    "gmkn": 1546, # nornikel gmk
    "astr": 557241, # astra
    "irao": 3003, #interraoao
    "lkoh": 128, #lukoil
    "vkco": 277441, # vk mkpao
    "rual": 74865, # rusal mkpao ok
    "moex": 1032, # mosbirzha
    "mtss": 122, # MTS
    "nvtk": 765, # novatek
    "pikk": 103, # pik ao
    "plzl": 3681, # polus
    "reni": 136463, # renessans straghovanie
    "rosn": 123, # rosneft
    "rtkm": 1577, # rostelecom
    "sber": "sberbank", # sberbank
    "svcb": "Sovcombank", # sovkombank
    "flot": 2575, # sovkomflot
    "sngs": 3694, # surgutneftegaz
    "tatn": 30, # tatneft
    "phor": 10836, # phosagro
    "hhru": 563827, # headhunter
    "posi": 271567, # iPositib
    "bspb": "BANKSPB", # Bank SPB
    "enpg": 88457, # En plus group
    "afks": 212, # systema ao afk
    "cbom": "MKB", # mkb moskow kredit bank
    "fees": 1831, # fsk eas fskfees
    "upro": 3677, #junipro
    "sibn": 125, # gazpromneft
    "cnru": 592375, # cian
    "gemc": 563503, # umg mkpao
    "aqua": 1840, # rusakva 
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
            try:
                result = asyncio.run(file_update(f"{ticker}", f"{emitent_id}"))
            except:
                continue
            results.append(result)
        return result
    except Exception as e:
        logger.error(f"File update task failed: {str(e)}")
        raise self.retry(countdown=60, max_retries=3, exc=e)