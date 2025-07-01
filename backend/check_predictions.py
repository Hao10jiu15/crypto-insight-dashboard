#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的检查脚本，用于验证不同货币的预测数据是否确实不同
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.market_data.models import Currency, PredictionModel, PricePrediction


def check_prediction_data():
    print("=== 检查价格预测数据差异 ===\n")

    # 获取所有货币
    currencies = Currency.objects.all()

    print(f"总共 {currencies.count()} 个货币:")
    for currency in currencies:
        print(f"- {currency.name} ({currency.coingecko_id})")

    print("\n=== 检查模型状态 ===")

    prediction_data = {}

    for currency in currencies:
        try:
            # 获取最新的活跃模型
            model = PredictionModel.objects.filter(
                currency=currency, is_active=True
            ).latest("version")

            # 获取预测数据
            predictions = PricePrediction.objects.filter(model_run=model).order_by(
                "time"
            )[
                :5
            ]  # 只取前5条用于比较

            print(f"\n{currency.name}:")
            print(f"  模型文件: {model.model_file_path}")
            print(
                f"  预测记录数: {PricePrediction.objects.filter(model_run=model).count()}"
            )

            if predictions.exists():
                first_pred = predictions.first()
                print(f"  首个预测: {first_pred.time} -> ${first_pred.predicted_price}")

                # 收集前3个预测值用于比较
                pred_values = [float(p.predicted_price.amount) for p in predictions[:3]]
                prediction_data[currency.coingecko_id] = pred_values
                print(f"  前3个预测值: {pred_values}")
            else:
                print(f"  ❌ 无预测数据")

        except PredictionModel.DoesNotExist:
            print(f"\n{currency.name}: ❌ 无活跃模型")

    print("\n=== 检查预测数据是否相同 ===")

    # 比较不同货币的预测数据
    currency_ids = list(prediction_data.keys())

    if len(currency_ids) >= 2:
        for i in range(len(currency_ids)):
            for j in range(i + 1, len(currency_ids)):
                curr1, curr2 = currency_ids[i], currency_ids[j]
                values1, values2 = prediction_data[curr1], prediction_data[curr2]

                # 检查是否完全相同
                if values1 == values2:
                    print(f"❌ {curr1} 和 {curr2} 的预测值完全相同!")
                else:
                    # 计算差异百分比
                    diff_pct = abs(values1[0] - values2[0]) / values1[0] * 100
                    print(f"✅ {curr1} 和 {curr2} 的预测值不同 (差异: {diff_pct:.2f}%)")

    print("\n=== 检查模型文件 ===")

    for currency in currencies:
        try:
            model = PredictionModel.objects.filter(
                currency=currency, is_active=True
            ).latest("version")

            file_exists = os.path.exists(model.model_file_path)
            file_size = os.path.getsize(model.model_file_path) if file_exists else 0

            print(
                f"{currency.name}: 文件{'存在' if file_exists else '不存在'}, 大小: {file_size} 字节"
            )

        except PredictionModel.DoesNotExist:
            print(f"{currency.name}: 无模型记录")


if __name__ == "__main__":
    check_prediction_data()
