import logging
from pathlib import Path
import polars as pl
from src.cbonds_api import get_last_price
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

def file_update(ticker: str, emitent_id):
    PROJECT_ROOT = Path(__file__).parent.parent
    try:
        CSV_FILE = PROJECT_ROOT / "data" / f"{ticker.lower()}.csv"
    except Exception as e:
        print(f"Error type: {e}")
        return
    login = settings.CBONDS_LOGIN
    password = settings.CBONDS_PASSWORD

    logger.info(f"Starting file update at {datetime.now()}")

    try:
        df = pl.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        return

    if df["date"].dtype == pl.Utf8:
        df = df.with_columns(pl.col("date").str.strptime(pl.Date, format="%Y-%m-%d", strict=False))

    try:
        dates_cbond, prices_cbond = get_last_price(login, password, emitent_id)
        logger.info(f"Fetched {len(dates_cbond)} records from CBonds API")
        # print(dates_cbond, prices_cbond)
    except Exception as e:
        logger.warning("No data received from CBonds API")
        return


    new_data = pl.DataFrame({
        "date": dates_cbond,
        "price": prices_cbond  # Keep as is, including None values
    }).with_columns(
        pl.col("price").cast(pl.Float64)  # Polars will convert None to null
    )

    if dates_cbond and isinstance(dates_cbond[0], str):
        # If dates are strings, parse them to Date
        new_data = new_data.with_columns(
            pl.col("date").str.strptime(pl.Date, format="%Y-%m-%d", strict=False)
        )
    else:
        # If dates are already datetime objects or Date type, ensure proper casting
        new_data = new_data.with_columns(
            pl.col("date").cast(pl.Date)
        )

    existing_dates = set(df["date"].to_list())
    new_dates = set(new_data["date"].to_list())

    dates_to_add = new_dates - existing_dates

    if not dates_to_add:
        logger.info("No new dates to add. File is up to date.")
        return
    else:
        logger.info(f"Adding {len(dates_to_add)} new dates to the file")
        new_rows = new_data.filter(pl.col("date").is_in(dates_to_add))
        updated_df = pl.concat([df, new_rows], how="vertical")

    updated_df = updated_df.sort("date")

    # Filling missing data
    min_date = updated_df["date"].min()
    max_date = updated_df["date"].max()

    print(min_date, "=====" ,max_date)
    
    # Generate complete date range
    complete_date_range = pl.date_range(
        start=min_date,
        end=max_date,
        interval="1d",
        eager=True
    ).alias("date")
    
    complete_df = pl.DataFrame({"date": complete_date_range})
    
    # Left join to fill all gaps
    updated_df = complete_df.join(
        updated_df,
        on="date",
        how="left"
    )


    updated_df = updated_df.unique(subset=["date"], keep="first")

    updated_df.write_csv(CSV_FILE)
    logger.info(f"Successfully updated {CSV_FILE} with {len(new_rows)} new records")
