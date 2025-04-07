import requests, json, re, sys, os

API = ""

def call_api(route, method, coin="", rate=""):
    link = f"https://api.ataix.kz{route}"
    headers = {
        "accept": "application/json",
        "X-API-Key": API
    }
    payload = {
        "symbol": coin,
        "side": "buy",
        "type": "limit",
        "quantity": 1,
        "price": rate
    }
    if method == "get":
        resp = requests.get(link, headers=headers, timeout=20)
    elif method == "post":
        resp = requests.post(link, headers=headers, json=payload, timeout=20)
    return resp.json() if resp.status_code == 200 else f"Error {resp.status_code}: {resp.text}"

def extract_currencies(data, key):
    tokens = re.findall(r'\b\w+\b', data)
    return {re.sub(r'[^a-zA-Zа-яА-Я]', '', tokens[i + 1]) for i in range(len(tokens)-1) if tokens[i] == key}

def extract_pairs(data, key):
    tokens = re.findall(r'\b\w+(?:/\w+)?\b', data)
    return [tokens[i + 1] for i in range(len(tokens)-1) if tokens[i] == key]

def extract_prices(data, key):
    pattern = rf'{key}[\s\W]*([-+]?\d*\.\d+|\d+)'
    return re.findall(pattern, data)

def persist_orders(records):
    path = "orders_data.json"
    existing = []
    if os.path.isfile(path):
        try:
            with open(path, "r") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            pass
    for rec in records:
        item = rec["result"]
        existing.append({
            "orderID": item["orderID"],
            "price": item["price"],
            "quantity": item["quantity"],
            "symbol": item["symbol"],
            "created": item["created"],
            "status": item.get("status", "NEW")
        })
    with open(path, "w") as f:
        json.dump(existing, f, indent=4)

print("=" * 60)
print(" Биржевой баланс в USDT по доступным валютам ")
print("=" * 60)
assets = extract_currencies(json.dumps(call_api("/api/symbols", "get")), "base")
for coin in assets:
    result = call_api(f"/api/user/balances/{coin}", "get")
    match = re.search(r"'available':\s*'([\d.]+)'", str(result))
    if match:
        print(f"{coin:<10} | {match.group(1):>10} USDT")
print("=" * 60)

print("\n Отфильтрованные пары с USDT и ценой не более 0.6 ")
print("=" * 60)
all_pairs = extract_pairs(json.dumps(call_api("/api/symbols", "get")), "symbol")
all_rates = extract_prices(json.dumps(call_api("/api/prices", "get")), "lastTrade")
filtered, prices_dict = [], {}
for idx in range(len(all_pairs)):
    if "USDT" in all_pairs[idx] and float(all_rates[idx]) <= 0.6:
        print(f"{all_pairs[idx]:<15} | {all_rates[idx]:>10} USDT")
        filtered.append(all_pairs[idx])
        prices_dict[all_pairs[idx]] = all_rates[idx]
print("=" * 60)

while True:
    choice = input("Выберите токен (например: TRX, IMX, 1INCH) или 'exit' --> ").upper()
    if choice + "/USDT" in filtered:
        base_price = prices_dict[choice + "/USDT"]
        break
    elif choice == "EXIT":
        sys.exit()
    else:
        print("[!] Пара не найдена. Повторите ввод.")

print(f"\nВыбран токен: {choice} с ценой {base_price} USDT")
discounts = [0.98, 0.95, 0.92]
levels = [round(float(base_price) * d, 4) for d in discounts]
print("\nСоздание ордеров на покупку по сниженной цене:")
for perc, val in zip([2, 5, 8], levels):
    print(f"- {perc}%: {val} USDT")

print("\nПодтвердите действие ('yes' или 'exit')")
while True:
    confirm = input("--> ")
    if confirm == "yes":
        break
    elif confirm == "exit":
        sys.exit()

orders = []
for level_price in levels:
    order_info = call_api("/api/orders", "post", choice + "/USDT", level_price)
    orders.append(order_info)

persist_orders(orders)
print("\n[+] Заказы созданы и сохранены в 'orders_data.json'.")
print("[i] Проверить можно на ATAIX в разделе 'Мои ордера'.")
print("=" * 60)
