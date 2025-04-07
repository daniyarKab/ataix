import json
import re
import requests

API_KEY = "___API___"

def extract_currencies(raw_text, keyword):
    tokens = re.findall(r'\b\w+\b', raw_text)
    currency_count = 0
    for idx in range(len(tokens) - 1):
        if tokens[idx] == keyword:
            val = re.sub(r'[^a-zA-Zа-яА-Я]', '', tokens[idx + 1])
            sep = '\n' if currency_count % 5 == 0 else ' '
            print(f"{currency_count + 1}) {val}", end=sep)
            currency_count += 1
    print(f"\n🔢 Всего валют: {currency_count}")

def extract_pairs(raw_text, keyword):
    tokens = re.findall(r'\b\w+(?:/\w+)?\b', raw_text)
    result_pairs = []
    pair_count = 0
    for i in range(len(tokens) - 1):
        if tokens[i] == keyword:
            next_val = tokens[i + 1]
            sep = '\n' if pair_count % 5 == 0 else '\t'
            print(f"{pair_count + 1}) {next_val}", end=sep)
            result_pairs.append(next_val)
            pair_count += 1
    print(f"\n🔢 Всего пар: {pair_count}")
    return result_pairs

def extract_prices(raw_text, keyword):
    regex = rf'{keyword}[\s\W]*([-+]?\d*\.\d+|\d+)'
    return re.findall(regex, raw_text)

def call_api(endpoint, method="get", symbol="", price=""):
    url = f"https://api.ataix.kz{endpoint}"
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
        response = requests.get(url, headers=headers, timeout=20)
    elif method == "post":
        response = requests.post(url, headers=headers, json=payload, timeout=20)
    else:
        return "❗ Неверный метод запроса"

    if response.status_code == 200:
        return response.json()
    return f"❌ Ошибка {response.status_code}: {response.text}"


print("🔍 Получение списка валют:")
raw_data = json.dumps(call_api("/api/currencies"))
extract_currencies(raw_data, "currency")

print("\n🔍 Получение списка торговых пар:")
symbols_list = extract_pairs(json.dumps(call_api("/api/symbols")), "symbol")

print("\n💸 Получение актуальных цен:")
prices = extract_prices(json.dumps(call_api("/api/prices")), "lastTrade")

print("\n📈 Символы и их цены:")
for idx, pair in enumerate(symbols_list):
    sep = '\n' if idx % 5 == 0 else '\t'
    print(f"{idx + 1}) {pair}: {prices[idx]}", end=sep)
