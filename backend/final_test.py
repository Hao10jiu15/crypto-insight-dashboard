import requests

currencies = ["bitcoin", "ethereum", "tether"]
for currency in currencies:
    response = requests.get(
        f"http://localhost:8000/api/forecasts/?currency_id={currency}"
    )
    print(f"{currency.capitalize()} API状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  返回条数: {len(data)}")
        if data:
            for i, item in enumerate(data[:3]):
                time_str = item.get("time", "")
                price = item.get("predicted_price", 0)
                print(f"    {i+1}: {time_str} -> ${float(price):.2f}")
    elif response.status_code == 404:
        print("  404: 无预测模型")
    else:
        print(f"  错误: {response.status_code}")
    print()
