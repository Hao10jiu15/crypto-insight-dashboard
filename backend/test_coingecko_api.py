#!/usr/bin/env python3
"""测试CoinGecko API返回的数据"""

import requests
import json


def test_coingecko_api():
    """测试CoinGecko API的markets端点"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": "bitcoin,ethereum",
        "order": "market_cap_desc",
        "per_page": 2,
        "page": 1,
        "sparkline": False,
    }

    try:
        response = requests.get(url, params=params)
        print(f"HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"返回数据条数: {len(data)}")

            if data:
                # 显示第一条数据的所有字段
                print("\n第一条数据的字段:")
                for key, value in data[0].items():
                    print(f"  {key}: {value}")

                # 检查volume_24h字段
                if "total_volume" in data[0]:
                    print(f"\n比特币24小时交易量: ${data[0]['total_volume']:,}")
                else:
                    print("\n⚠️ 没有找到volume字段")

        else:
            print(f"API错误: {response.text}")

    except Exception as e:
        print(f"请求失败: {e}")


if __name__ == "__main__":
    test_coingecko_api()
