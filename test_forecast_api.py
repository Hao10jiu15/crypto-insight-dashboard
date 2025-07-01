#!/usr/bin/env python
import requests
import json


def test_forecast_api():
    """测试预测API，检查是否只返回未来3天的数据"""

    currencies = ["bitcoin", "ethereum", "tether"]

    for currency in currencies:
        print(f"\n=== 测试 {currency} 预测API ===")
        try:
            response = requests.get(
                f"http://localhost:8000/api/forecast/?currency_id={currency}",
                timeout=10,
            )
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"返回数据条数: {len(data)}")

                if data:
                    print("预测数据:")
                    for i, item in enumerate(data[:5]):  # 显示前5条
                        time_str = item.get("time", "未知时间")
                        price = item.get("predicted_price", 0)
                        print(f"  {i+1}: {time_str} -> ${price:.2f}")
                else:
                    print("  无预测数据")

            elif response.status_code == 404:
                print("  404: 未找到预测模型（可能是稳定币）")
            else:
                print(f"  错误: {response.text}")

        except Exception as e:
            print(f"  请求失败: {e}")


if __name__ == "__main__":
    test_forecast_api()
