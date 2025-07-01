#!/usr/bin/env python3
"""测试Tether的新预测数据"""

import requests

print("测试Tether的预测API:")

# 普通预测API
response = requests.get("http://localhost:8000/api/forecasts/?currency_id=tether")
print(
    f"普通预测API: {response.status_code}, 数据条数: {len(response.json()) if response.status_code == 200 else 'N/A'}"
)

# 完整预测API
response = requests.get(
    "http://localhost:8000/api/forecasts/?currency_id=tether&include_historical=true"
)
print(
    f"完整预测API: {response.status_code}, 数据条数: {len(response.json()) if response.status_code == 200 else 'N/A'}"
)

# 检查数据详情
if response.status_code == 200:
    data = response.json()
    if len(data) > 0:
        print(f"时间范围: {data[0]['time']} 到 {data[-1]['time']}")
        print("最后3条预测:")
        for i, item in enumerate(data[-3:]):
            price = float(item["predicted_price"])
            print(f"  {i+1}: {item['time']} -> ${price:.6f}")
