import requests


def get_last_price(login:str, password:str, emitent_id:str):
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

    resp = requests.get(
        MAIN_URL,
        json=payload,
        timeout=90,
        verify=False
    )
    resp.encoding = "utf-8"
    resp.raise_for_status()
    data = resp.json()

    trading_dates = []
    last_prices = []

    for d in data["items"]:
        trading_dates.append(d["trading_date"])
        last_prices.append(d["last_price"])
        
    return trading_dates, last_prices
