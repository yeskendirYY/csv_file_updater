import logging
import os
from pathlib import Path
import polars as pl
from cbonds_api import get_last_price
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

def file_update(ticker: str, emitent_id):
    PROJECT_ROOT = Path(__file__).parent.parent
    CSV_FILE = PROJECT_ROOT / "data" / f"{ticker.lower()}.csv"

    logger.info(f"Starting file update at {datetime.now()}")

    try:
        df = pl.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")

    last = df.tail(1).to_dicts()[0]
   
    date_file = last["date"]
    last_price_file = last["price"]


    login = settings.CBONDS_LOGIN
    password = settings.CBONDS_PASSWORD
    # emitent_id = emitent_id

    dates, prices = get_last_price(login, password, emitent_id)
    print(dates, prices)

    date_cbond = dates[0]
    last_price_cbond = prices[0]


    if date_file != date_cbond:
        print("incorrect")
        new_row = pl.DataFrame({
            "date": date_cbond,
            "price": float(last_price_cbond)
        })
        updated_csv = pl.concat([df, new_row])
        updated_csv.write_csv(CSV_FILE)
    else:
        print("correct")

