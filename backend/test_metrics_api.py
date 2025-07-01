#!/usr/bin/env python3
"""测试修复后的metrics API"""

import requests

BASE_URL = "http://localhost:8000"


def test_metrics_api():
    """测试货币指标API"""
    currencies = ["bitcoin", "ethereum", "cardano"]

    for currency in currencies:
        print(f"\n{currency.upper()} 指标数据:")
        try:
            response = requests.get(f"{BASE_URL}/api/metrics/{currency}/")
            print(f"  API状态: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                current_price = data.get("current_price", 0)
                market_cap = data.get("market_cap", 0)
                volume_24h = data.get("volume_24h", 0)
                price_change = data.get("price_change_percentage_24h", 0)

                print(f"  当前价格: ${current_price:,.2f}")
                print(f"  市值: ${market_cap:,.0f}")
                print(f"  24h交易量: ${volume_24h:,.0f}")
                print(f"  24h价格变化: {price_change:.2f}%")
            else:
                print(f"  错误: {response.text}")

        except Exception as e:
            print(f"  异常: {e}")


if __name__ == "__main__":
    test_metrics_api()
