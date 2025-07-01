#!/usr/bin/env python3
"""清除Django缓存并测试API"""

import requests

BASE_URL = "http://localhost:8000"


def clear_cache_and_test():
    """清除缓存并测试"""
    # 先清除缓存（通过添加时间戳参数强制刷新）
    import time

    timestamp = int(time.time())

    currency = "bitcoin"
    print(f"测试 {currency} 的指标数据:")

    try:
        # 添加时间戳参数强制绕过缓存
        response = requests.get(f"{BASE_URL}/api/metrics/{currency}/?t={timestamp}")
        print(f"API状态: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("返回的完整数据:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"错误: {response.text}")

    except Exception as e:
        print(f"异常: {e}")


if __name__ == "__main__":
    clear_cache_and_test()
