import os
import sys
import django

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.market_data.models import MarketData, Currency
import pandas as pd

# 检查不同货币的数据频率
currencies = ["bitcoin", "ethereum"]
for currency_id in currencies:
    currency = Currency.objects.get(coingecko_id=currency_id)
    data = MarketData.objects.filter(currency=currency).order_by("time").values("time")
    df = pd.DataFrame(list(data))
    print(f"\n{currency.name}:")
    print(f"  数据条数: {len(df)}")
    if len(df) > 1:
        df["time_diff"] = df["time"].diff()
        most_common_interval = df["time_diff"].mode()
        if not most_common_interval.empty:
            print(f"  最常见间隔: {most_common_interval.iloc[0]}")
        print(f"  最新3条数据:")
        for i, time in enumerate(df["time"].tail(3)):
            print(f"    {i+1}: {time}")
