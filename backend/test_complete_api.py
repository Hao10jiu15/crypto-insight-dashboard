import requests

# 测试完整预测数据API
currencies = ["bitcoin", "ethereum"]
for currency in currencies:
    print(f"\n=== 测试 {currency} ===")

    # 测试默认API（只返回未来数据）
    response = requests.get(
        f"http://localhost:8000/api/forecasts/?currency_id={currency}"
    )
    if response.status_code == 200:
        data = response.json()
        print(f"默认API返回: {len(data)} 条数据")
    else:
        print(f"默认API错误: {response.status_code}")

    # 测试完整数据API（包含历史数据）
    response = requests.get(
        f"http://localhost:8000/api/forecasts/?currency_id={currency}&include_historical=true"
    )
    if response.status_code == 200:
        data = response.json()
        print(f"完整API返回: {len(data)} 条数据")
        if data:
            print(f"  时间范围: {data[0]['time']} 到 {data[-1]['time']}")
    else:
        print(f"完整API错误: {response.status_code}")
