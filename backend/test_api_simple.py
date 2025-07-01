#!/usr/bin/env python
import requests

# 测试Bitcoin预测API
try:
    response = requests.get("http://localhost:8000/api/forecasts/?currency_id=bitcoin")
    print(f"Bitcoin API状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"返回条数: {len(data)}")
        if data:
            for i, item in enumerate(data[:3]):
                print(
                    f'  {i+1}: {item.get("time")} -> ${item.get("predicted_price", 0):.2f}'
                )
    else:
        print(f"错误: {response.text}")

    # 测试Ethereum API
    response = requests.get("http://localhost:8000/api/forecasts/?currency_id=ethereum")
    print(f"Ethereum API状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"返回条数: {len(data)}")
        if data:
            for i, item in enumerate(data[:3]):
                print(
                    f'  {i+1}: {item.get("time")} -> ${item.get("predicted_price", 0):.2f}'
                )
    else:
        print(f"错误: {response.text}")

except Exception as e:
    print(f"请求失败: {e}")
