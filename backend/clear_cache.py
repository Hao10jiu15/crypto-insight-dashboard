# -*- coding: utf-8 -*-
"""
清除预测缓存的简单脚本
"""
import os
import sys

# 添加项目路径
sys.path.append("/d/crypto-insight-dashboard/backend")

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    import django

    django.setup()

    from django.core.cache import cache
    from apps.market_data.models import Currency, PredictionModel, PricePrediction

    print("=== 清除预测相关缓存 ===")

    # 手动清除已知的缓存键模式
    currencies = Currency.objects.all()

    cleared_count = 0
    for currency in currencies:
        # 清除预测数据缓存
        for hour in range(24):
            for version in range(1, 10):  # 假设版本不超过10
                keys_to_clear = [
                    f"forecast_data_{currency.coingecko_id}_v{version}_20250630_{hour:02d}",
                    f"forecast_components_{currency.coingecko_id}_v{version}_20250630_{hour:02d}",
                    f"forecast_data_{currency.coingecko_id}_20250630_{hour:02d}",
                    f"forecast_components_{currency.coingecko_id}_20250630_{hour:02d}",
                ]

                for key in keys_to_clear:
                    if cache.get(key) is not None:
                        cache.delete(key)
                        cleared_count += 1
                        print(f"清除缓存: {key}")

    # 清除通用模式
    cache.clear()  # 清除所有缓存

    print(f"✅ 已清除 {cleared_count} 个特定缓存键")
    print("✅ 已清除所有缓存")

    print("\n=== 当前预测数据状态 ===")
    for currency in currencies:
        try:
            model = PredictionModel.objects.filter(
                currency=currency, is_active=True
            ).latest("version")
            pred_count = PricePrediction.objects.filter(model_run=model).count()
            print(f"{currency.name}: 版本 {model.version}, {pred_count} 条预测")
        except PredictionModel.DoesNotExist:
            print(f"{currency.name}: 无模型")

except Exception as e:
    print(f"错误: {e}")
    import traceback

    traceback.print_exc()
