import os
import requests
from celery import shared_task
from datetime import datetime, timezone as dt_timezone
from decimal import Decimal
from django.utils import timezone

from apps.market_data.models import Currency, MarketData

COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_historical_data_for_coin(self, currency_id):
    """
    获取并存储单个加密货币的历史市场数据的Celery任务。
    处理交易量和时区信息。
    """
    try:
        currency = Currency.objects.get(id=currency_id)
        print(f"开始获取 {currency.name} 的数据...")

        url = f"{COINGECKO_BASE_URL}/coins/{currency.coingecko_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "30",
            "interval": "daily",
            "x_cg_demo_api_key": COINGECKO_API_KEY,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # 将交易量数据转换成一个以时间戳为键的字典，方便快速查找
        volumes_dict = {item[0]: item[1] for item in data.get("total_volumes", [])}

        # 遍历价格数据，并从字典中匹配对应的交易量
        for price_point in data.get("prices", []):
            timestamp, price = price_point

            # 从字典中获取交易量，如果找不到则默认为0
            volume = volumes_dict.get(timestamp, 0)

            # CoinGecko的时间戳是UTC标准的毫秒时间戳，需要处理时区
            naive_record_time = datetime.fromtimestamp(timestamp / 1000)
            # 创建一个UTC时区的感知型datetime对象
            aware_record_time = timezone.make_aware(naive_record_time, dt_timezone.utc)

            # 使用 update_or_create 确保数据可以被更新
            MarketData.objects.update_or_create(
                currency=currency,
                time=aware_record_time,
                defaults={
                    "open": Decimal(price),
                    "high": Decimal(price),
                    "low": Decimal(price),
                    "close": Decimal(price),
                    "volume": Decimal(volume),  # 使用交易量数据
                },
            )

        print(f"成功完成 {currency.name} 的数据获取。")
        return f"Successfully fetched data for {currency.name}"

    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 429:
            print(f"遭遇速率限制，将在 {self.default_retry_delay} 秒后重试...")
            raise self.retry(exc=exc)
        print(f"获取 {currency.name} 数据时发生HTTP错误: {exc}")
        return f"Failed to fetch data for {currency.name} due to HTTPError: {exc}"
    except Exception as exc:
        print(f"获取 {currency.name} 数据时发生未知错误，将重试: {exc}")
        raise self.retry(exc=exc)


@shared_task
def dispatch_market_data_updates():
    """
    分发器任务。
    """
    currencies = Currency.objects.all()
    print(f"开始分发数据更新任务，共找到 {len(currencies)} 种货币。")
    for currency in currencies:
        fetch_historical_data_for_coin.delay(currency.id)
    print("所有数据更新任务已成功分发。")
