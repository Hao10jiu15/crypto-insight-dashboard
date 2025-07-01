# -*- coding: utf-8 -*-
"""
测试不同货币的API响应，特别是稳定币的处理
"""
import requests
import json


def test_currency_predictions():
    """测试不同货币的预测数据API响应"""
    base_url = "http://localhost:8000/api"

    # 测试的货币列表
    test_currencies = ["bitcoin", "ethereum", "tether"]

    print("=== 测试各货币的预测数据 ===\n")

    for currency_id in test_currencies:
        print(f"测试 {currency_id.upper()}")
        print("-" * 40)

        try:
            # 测试预测数据
            forecast_url = f"{base_url}/forecasts/?currency_id={currency_id}"
            response = requests.get(forecast_url)

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取预测数据")
                print(f"   数据条数: {len(data)}")
                if data:
                    first_prediction = data[0]
                    print(
                        f"   首个预测: {first_prediction['predicted_price']} ({first_prediction['time']})"
                    )
                else:
                    print("   ⚠️  数据为空")

            elif response.status_code == 404:
                error_data = response.json()
                print(f"❌ 未找到预测模型")
                print(f"   错误信息: {error_data.get('error', '未知错误')}")

            else:
                print(f"❌ API错误: {response.status_code}")
                print(f"   响应: {response.text}")

        except Exception as e:
            print(f"❌ 请求失败: {e}")

        print()

    print("=== 总结 ===")
    print("Bitcoin: 应该有预测数据 (约$108k)")
    print("Ethereum: 应该有预测数据 (约$2.7k)")
    print("Tether: 应该返回404错误 (稳定币，无预测模型)")


if __name__ == "__main__":
    test_currency_predictions()
