#!/usr/bin/env python3
"""测试完整预测数据API"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_complete_forecast_api():
    """测试完整预测数据API (include_historical=true)"""
    currencies = ["bitcoin", "ethereum", "tether"]

    for currency in currencies:
        print(f"\n{currency.upper()} 完整预测数据:")
        try:
            # 测试完整预测数据API
            response = requests.get(
                f"{BASE_URL}/api/forecasts/?currency_id={currency}&include_historical=true"
            )
            print(f"  API状态: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  返回条数: {len(data)}")

                if len(data) > 0:
                    # 显示前3条和后3条数据，看时间范围
                    print("  前3条:")
                    for i, item in enumerate(data[:3]):
                        price = float(item["predicted_price"])
                        print(f"    {i+1}: {item['time']} -> ${price:.2f}")

                    if len(data) > 6:
                        print("  ... (中间数据略) ...")

                    print("  后3条:")
                    for i, item in enumerate(data[-3:]):
                        price = float(item["predicted_price"])
                        print(f"    {len(data)-2+i}: {item['time']} -> ${price:.2f}")

                    # 检查时间范围
                    first_date = data[0]["time"]
                    last_date = data[-1]["time"]
                    print(f"  时间范围: {first_date} 到 {last_date}")
                else:
                    print("  无数据")
            else:
                print(f"  错误: {response.text}")

        except Exception as e:
            print(f"  异常: {e}")


if __name__ == "__main__":
    test_complete_forecast_api()
