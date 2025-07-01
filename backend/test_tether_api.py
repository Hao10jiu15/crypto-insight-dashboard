#!/usr/bin/env python3
"""测试Tether预测API"""

import requests

BASE_URL = "http://localhost:8000"


def test_tether_forecast():
    """测试Tether预测API的稳定币检测"""
    print("测试Tether预测API:")

    # 测试普通预测API
    response = requests.get(f"{BASE_URL}/api/forecasts/?currency_id=tether")
    print(f"普通预测API状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"返回数据条数: {len(data)}")
    elif response.status_code == 404:
        print("返回404 - 正确识别为稳定币")
    else:
        print(f"错误响应: {response.text}")

    print()

    # 测试完整预测API
    response = requests.get(
        f"{BASE_URL}/api/forecasts/?currency_id=tether&include_historical=true"
    )
    print(f"完整预测API状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"返回数据条数: {len(data)}")
    elif response.status_code == 404:
        print("返回404 - 正确识别为稳定币")
    else:
        print(f"错误响应: {response.text}")


if __name__ == "__main__":
    test_tether_forecast()
