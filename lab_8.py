import json
import requests

API_KEY = ""

def get_request(endpoint, get_post_delete, symbol="", side="", price=""):
    url = f"https://api.ataix.kz{endpoint}"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    data = {
        "symbol": symbol,
        "side": side,
        "type": "limit",
        "quantity": 1,
        "price": price
    }

    if get_post_delete == "get":
        response = requests.get(url, headers=headers, timeout=20)
    elif get_post_delete == "post":
        response = requests.post(url, headers=headers, json=data, timeout=20)
    elif get_post_delete == "delete":
        response = requests.delete(url, headers=headers, timeout=20)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Ошибка: {response.status_code}, {response.text}"

# Загружаем исходные ордера
with open("orders_data.json", "r") as f:
    orders = json.load(f)

order_id_list = [r["orderID"] for r in orders if "orderID" in r]
symbols_list = [r["symbol"] for r in orders if "symbol" in r]
price_list = [float(r["price"]) for r in orders if "price" in r]
side_list = [r["side"] for r in orders if "side" in r]
status_list = [r["status"] for r in orders if "status" in r]
com_list = [float(r["commission"]) for r in orders if "commission" in r]

for i in range(len(order_id_list)):
    response = get_request(f"/api/orders/{order_id_list[i]}", "get")

sum_price_buy= round(sum(price_list[:3]), 4)
sum_com_buy= round(sum(com_list[:3]), 4)

sum_price_sell= round(sum(price_list[3:]), 4)
sum_com_sell= round(sum(com_list[3:]), 4)

print("\n[=] Текущие ордера:")
print("Order ID : Symbols : Price : Side : Commission : Status")
for o_id, sym, price, side, com, stat in zip(order_id_list, symbols_list, price_list, side_list, com_list, status_list):
    print(f"{o_id} : {sym} : {price} : {side} : {com} : {stat}")

print(f"\nОбщая сумма по покупке: {sum_price_buy}$ (комиссия: {sum_com_buy}$)")
print(f"Общая сумма по продаже: {sum_price_sell}$ (комиссия: {sum_com_sell}$)")

revenue = sum_price_sell - sum_com_sell
cost = sum_price_buy + sum_com_buy
total = round(revenue - cost, 4)

if cost != 0:
    total_percent = round((total / cost) * 100, 2)
else:
    total_percent = 0.0

print(f"Итог: {total}$ ({total_percent}%)")
