import httpx
import asyncio

async def get_last_price(login:str, password:str, emitent_id:str):
    MAIN_URL = (f"https://ws.cbonds.info/services/json/get_tradings_stocks_full_new/?lang=rus")

    payload = {
        "auth": {"login":f"{login}","password":f"{password}"},
        "filters": [
            {"field": "emitent_id", "operator": "eq", "value": f"{emitent_id}"}
        ],
        "quantity": {"limit": 500, "offset": 0},
        "sorting": [
            {"field": "trading_date", "order": "desc"}
            ],
        "fields": [
            {"field": "trading_date"},
            {"field": "last_price"}
        ]
    }

    # resp = await requests.get(
    #     MAIN_URL,
    #     json=payload,
    #     timeout=150,
    #     verify=False
    # )
    # resp.encoding = "utf-8"
    # resp.raise_for_status()
    # data = resp.json()

    async with httpx.AsyncClient(verify=False, timeout=150) as client:
        resp = await client.get(MAIN_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()

    await asyncio.sleep(5)

    trading_dates = []
    last_prices = []

    for d in data["items"]:
        trading_dates.append(d["trading_date"])
        last_prices.append(d["last_price"])
        
    return trading_dates, last_prices
