# -*- coding: utf-8 -*-
import requests
import json


def test_api_endpoints():
    """测试API端点是否返回不同货币的不同预测数据"""

    base_url = "http://localhost:8000/api"

    # 首先获取货币列表
    try:
        currencies_response = requests.get(f"{base_url}/currencies/")
        if currencies_response.status_code != 200:
            print(f"无法获取货币列表: {currencies_response.status_code}")
            return

        currencies = currencies_response.json()
        print(f"找到 {len(currencies)} 个货币")

        if len(currencies) < 2:
            print("货币数量不足，无法比较")
            return

        prediction_samples = {}

        # 获取每个货币的预测数据
        for currency in currencies[:3]:  # 只测试前3个货币
            coingecko_id = currency["coingecko_id"]
            name = currency["name"]

            print(f"\n检查 {name} ({coingecko_id}) 的预测数据...")

            try:
                forecast_response = requests.get(
                    f"{base_url}/forecasts/", params={"currency_id": coingecko_id}
                )

                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    if forecast_data and len(forecast_data) > 0:
                        # 取前3个预测值进行比较
                        sample_values = [
                            item["predicted_price"] for item in forecast_data[:3]
                        ]
                        prediction_samples[coingecko_id] = {
                            "name": name,
                            "values": sample_values,
                            "total_predictions": len(forecast_data),
                        }
                        print(f"  ✅ 获得 {len(forecast_data)} 条预测")
                        print(f"  前3个预测值: {sample_values}")
                    else:
                        print(f"  ❌ 无预测数据")
                else:
                    print(f"  ❌ API错误: {forecast_response.status_code}")
                    print(f"  错误信息: {forecast_response.text}")

            except Exception as e:
                print(f"  ❌ 请求失败: {e}")

        # 比较不同货币的预测值
        print(f"\n=== 比较预测数据 ===")

        currency_ids = list(prediction_samples.keys())
        if len(currency_ids) >= 2:
            for i in range(len(currency_ids)):
                for j in range(i + 1, len(currency_ids)):
                    curr1, curr2 = currency_ids[i], currency_ids[j]
                    data1, data2 = prediction_samples[curr1], prediction_samples[curr2]

                    name1, name2 = data1["name"], data2["name"]
                    values1, values2 = data1["values"], data2["values"]

                    if values1 == values2:
                        print(f"❌ {name1} 和 {name2} 的预测值完全相同!")
                        print(f"   值: {values1}")
                    else:
                        if values1 and values2:
                            diff_pct = (
                                abs(float(values1[0]) - float(values2[0]))
                                / float(values1[0])
                                * 100
                            )
                            print(
                                f"✅ {name1} 和 {name2} 的预测值不同 (差异: {diff_pct:.2f}%)"
                            )
                        else:
                            print(f"⚠️  {name1} 和 {name2} 有空预测值")

        # 打印详细信息
        print(f"\n=== 详细数据 ===")
        for curr_id, data in prediction_samples.items():
            print(f"{data['name']} ({curr_id}):")
            print(f"  总预测数: {data['total_predictions']}")
            print(f"  示例值: {data['values']}")

    except Exception as e:
        print(f"测试失败: {e}")


if __name__ == "__main__":
    test_api_endpoints()
