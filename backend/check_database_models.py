#!/usr/bin/env python3
"""检查数据库中的预测模型状态"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.market_data.models import Currency, PredictionModel, PricePrediction

print("=== 数据库中的货币和模型状态 ===")

currencies = Currency.objects.all()
print(f"总共有 {currencies.count()} 个货币")

for currency in currencies:
    print(f"\n{currency.name} ({currency.coingecko_id}):")

    # 检查是否有活跃模型
    try:
        latest_model = PredictionModel.objects.filter(
            currency=currency, is_active=True
        ).latest("version")
        print(f"  ✅ 有活跃模型 - 版本: {latest_model.version}")

        # 检查预测数据数量
        pred_count = PricePrediction.objects.filter(model_run=latest_model).count()
        future_pred_count = PricePrediction.objects.filter(
            model_run=latest_model, time__gt=django.utils.timezone.now()
        ).count()
        print(f"  📊 预测数据: 总共 {pred_count} 条, 未来 {future_pred_count} 条")

    except PredictionModel.DoesNotExist:
        print(f"  ❌ 没有活跃模型")
