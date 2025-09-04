import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # ✅ Works in Docker
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://{REDIS_HOST}:{REDIS_PORT}/0")
    ROOT_PATH = os.getenv("ROOT_PATH")
    CBONDS_LOGIN = os.getenv("LOGIN_CBONDS")
    CBONDS_PASSWORD = os.getenv("PASSWORD_CBONDS")

    FILE_UPDATE_INTERVAL_MINUTES = 5
    DAILY_REPORT_HOUR = 9 # 9 AM

settings = Settings()