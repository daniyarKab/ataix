import json
import requests
import os

API_KEY = ""

def send_limit_order(symbol, side, price):
    endpoint = "https://api.ataix.kz/api/orders"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    payload = {
        "symbol": symbol,
        "side": side,
        "type": "limit",
        "quantity": 1,
        "price": price
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Ошибка {response.status_code}] {response.text}")
            return None
    except Exception as err:
        print("[!] Не удалось подключиться:", err)
        return None

def update_order_log(entries):
    file_name = "orders_data.json"
    try:
        if os.path.isfile(file_name):
            with open(file_name, "r") as f:
                existing = json.load(f)
        else:
            existing = []
    except:
        existing = []

    for entry in entries:
        if entry and "result" in entry:
            info = entry["result"]
            existing.append({
                "orderID": info.get("orderID"),
                "symbol": info.get("symbol"),
                "price": info.get("price"),
                "quantity": info.get("quantity"),
                "side": info.get("side"),
                "created": info.get("created"),
                "status": info.get("status", "NEW")
            })

    with open(file_name, "w") as f:
        json.dump(existing, f, indent=4)

def sell_with_markup(pairs, base_rates):
    placed_orders = []
    for idx, pair in enumerate(pairs):
        sell_price = round(base_rates[idx] * 1.02, 4)
        result = send_limit_order(pair, "sell", sell_price)
        placed_orders.append(result)
    return placed_orders

# Загрузка существующих ордеров
with open("orders_data.json", "r") as f:
    records = json.load(f)

symbols_list = [r["symbol"] for r in records if "symbol" in r]
price_list = [float(r["price"]) for r in records if "price" in r]

print("\n[=] Текущие ордера:")
for s, p in zip(symbols_list, price_list):
    print(f" - {s}: {p} USD")

new_orders = sell_with_markup(symbols_list, price_list)
update_order_log(new_orders)

print("\n[+] Созданы ордера на продажу:")
for sym, base_price in zip(symbols_list, price_list):
    final_price = round(base_price * 1.02, 4)
    print(f" - {sym} по {final_price} USD")
