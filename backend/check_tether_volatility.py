#!/usr/bin/env python3
"""检查Tether的价格波动情况"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.market_data.models import Currency, MarketData

try:
    tether = Currency.objects.get(coingecko_id="tether")
    print(f"Tether货币: {tether.name}")

    # 获取最近100条数据
    market_data = MarketData.objects.filter(currency=tether).order_by("-time")[:100]
    print(f"市场数据条数: {market_data.count()}")

    if market_data.exists():
        prices = [float(data.close.amount) for data in market_data]
        price_range = max(prices) - min(prices)
        avg_price = sum(prices) / len(prices)
        volatility = price_range / avg_price if avg_price > 0 else 0

        print(f"价格范围: ${min(prices):.6f} - ${max(prices):.6f}")
        print(f"平均价格: ${avg_price:.6f}")
        print(f"价格变化范围: ${price_range:.6f}")
        print(f"波动率: {volatility:.6f} ({volatility*100:.2f}%)")
        print(f"是否为稳定币 (波动率<1%): {volatility < 0.01}")

        # 显示最近5条数据
        print("\n最近5条价格数据:")
        for i, data in enumerate(market_data[:5]):
            print(f"  {i+1}: {data.time} -> ${float(data.close.amount):.6f}")
    else:
        print("没有市场数据")

except Currency.DoesNotExist:
    print("未找到Tether货币")
except Exception as e:
    print(f"错误: {e}")
