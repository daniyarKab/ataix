import json
import os, sys
import requests

API_KEY = ""


def send_api_request(endpoint, method, symbol="", price=""):
    base_url = f"https://api.ataix.kz{endpoint}"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    payload = {
        "symbol": symbol,
        "side": "buy",
        "type": "limit",
        "quantity": 1,
        "price": price
    }

    if method == "get":
        response = requests.get(base_url, headers=headers, timeout=20)
    elif method == "post":
        response = requests.post(base_url, headers=headers, json=payload, timeout=20)
    elif method == "delete":
        response = requests.delete(base_url, headers=headers, timeout=20)
    else:
        raise ValueError("Unsupported HTTP method")

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"


def append_orders_to_file(orders):
    filename = "orders_data.json"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                existing_orders = json.load(file)
            except json.JSONDecodeError:
                existing_orders = []
    else:
        existing_orders = []

    for order in orders:
        order_info = {
            "orderID": order["result"]["orderID"],
            "price": order["result"]["price"],
            "quantity": order["result"]["quantity"],
            "symbol": order["result"]["symbol"],
            "created": order["result"]["created"],
            "status": order["result"].get("status", "NEW")
        }
        existing_orders.append(order_info)

    with open(filename, "w") as file:
        json.dump(existing_orders, file, indent=4)


with open("orders_data.json", "r") as file:
    order_data = json.load(file)

order_ids = [entry["orderID"] for entry in order_data if "orderID" in entry]
order_prices = [entry["price"] for entry in order_data if "price" in entry]
order_symbols = [entry["symbol"] for entry in order_data if "symbol" in entry]
order_statuses = [entry["status"] for entry in order_data if "status" in entry]

pending_order_ids = []
pending_order_prices = []

print("=" * 50)
print("ORDER STATUS OVERVIEW")
print("=" * 50)
for idx, order_id in enumerate(order_ids):
    print(f"OrderID: {order_id}\t Status: {order_statuses[idx]}")

print("-" * 50)
print("If an order is filled, status will be 'filled'. Otherwise it will be updated to 'cancelled'.")
print("-" * 50)

is_filled = False
for idx, order_id in enumerate(order_ids):
    order_status_response = send_api_request(f"/api/orders/{order_id}", "get")

    if "filled" in str(order_status_response):
        for entry in order_data:
            if entry["orderID"] == order_id:
                entry["status"] = "filled"
        is_filled = True
    else:
        print(f"OrderID: {order_id}\t Price: {order_prices[idx]}$\t Status: {order_statuses[idx]}")
        pending_order_ids.append(order_id)
        pending_order_prices.append(order_prices[idx])
        for entry in order_data:
            if entry["orderID"] == order_id:
                entry["status"] = "cancelled"

    with open("orders_data.json", "w", encoding="utf-8") as file:
        json.dump(order_data, file, indent=4, ensure_ascii=False)

if is_filled:
    print("All orders done!")
    sys.exit()

print("=" * 50)
print("CANCELLING UNFILLED ORDERS")
print("=" * 50)
for order_id in pending_order_ids:
    send_api_request(f"/api/orders/{order_id}", "delete")
    print(f"[-] Cancelled Order: {order_id}")

print("=" * 50)
print("REPLACING ORDERS WITH +1% PRICE")
print("=" * 50)
new_orders = []
for idx, order_id in enumerate(pending_order_ids):
    updated_price = round(float(pending_order_prices[idx]) * 1.01, 4)
    new_order = send_api_request("/api/orders", "post", order_symbols[idx], updated_price)
    new_orders.append(new_order)
    print(f"[+] New Order Created: {order_symbols[idx]} at {updated_price}$")

append_orders_to_file(new_orders)
print("=" * 50)
print("[+] Orders successfully recreated and saved.")
print("[+] Visit ATAIX > My Orders for confirmation.")
print("=" * 50)
