#!/usr/bin/env python3
"""检查Tether是否有预测模型"""

import requests

BASE_URL = "http://localhost:8000"


def check_currency_models():
    """检查所有货币的模型状态"""
    currencies = ["bitcoin", "ethereum", "tether"]

    for currency in currencies:
        print(f"\n{currency.upper()}:")

        # 检查是否有模型
        response = requests.get(f"{BASE_URL}/api/forecasts/?currency_id={currency}")
        print(
            f"  普通预测API: {response.status_code} (数据条数: {len(response.json()) if response.status_code == 200 else 'N/A'})"
        )

        # 检查完整模型
        response = requests.get(
            f"{BASE_URL}/api/forecasts/?currency_id={currency}&include_historical=true"
        )
        print(
            f"  完整预测API: {response.status_code} (数据条数: {len(response.json()) if response.status_code == 200 else 'N/A'})"
        )


if __name__ == "__main__":
    check_currency_models()
