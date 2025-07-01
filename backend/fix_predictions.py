"""
简单的数据库清理和重训练脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.market_data.models import Currency, PredictionModel, PricePrediction
from apps.ml_predictions.tasks import train_and_predict_task
import time


def main():
    print("=== 开始修复预测数据问题 ===")

    # 1. 清除现有预测数据
    print("1. 清除现有预测数据...")
    pred_deleted = PricePrediction.objects.all().delete()
    print(f"   删除了 {pred_deleted[0]} 条预测记录")

    model_deleted = PredictionModel.objects.all().delete()
    print(f"   删除了 {model_deleted[0]} 条模型记录")

    # 2. 获取所有货币
    currencies = Currency.objects.all()
    print(f"2. 找到 {currencies.count()} 个货币需要训练")

    # 3. 首先训练比特币
    try:
        bitcoin = Currency.objects.get(coingecko_id="bitcoin")
        print(f"3. 训练比特币模型: {bitcoin.name}")
        train_and_predict_task(bitcoin.id)
        print("   ✅ 比特币模型训练完成")
        time.sleep(2)  # 等待数据写入
    except Currency.DoesNotExist:
        print("   ❌ 没有找到比特币")
    except Exception as e:
        print(f"   ❌ 比特币训练失败: {e}")

    # 4. 训练其他货币
    other_currencies = currencies.exclude(coingecko_id="bitcoin")
    print(f"4. 训练其他 {other_currencies.count()} 个货币的模型")

    for i, currency in enumerate(other_currencies, 1):
        try:
            print(f"   [{i}/{other_currencies.count()}] 训练 {currency.name}")
            train_and_predict_task(currency.id)
            print(f"   ✅ {currency.name} 训练完成")
        except Exception as e:
            print(f"   ❌ {currency.name} 训练失败: {e}")

    # 5. 验证结果
    print("5. 验证训练结果...")

    prediction_samples = {}

    for currency in currencies:
        try:
            model = PredictionModel.objects.filter(
                currency=currency, is_active=True
            ).latest("version")
            pred_count = PricePrediction.objects.filter(model_run=model).count()

            # 获取前3个预测值用于比较
            predictions = PricePrediction.objects.filter(model_run=model).order_by(
                "time"
            )[:3]

            if predictions.exists():
                pred_values = [float(p.predicted_price.amount) for p in predictions]
                prediction_samples[currency.coingecko_id] = {
                    "name": currency.name,
                    "values": pred_values,
                    "count": pred_count,
                }
                print(
                    f"   {currency.name}: {pred_count} 条预测, 前3个值: {pred_values}"
                )
            else:
                print(f"   {currency.name}: {pred_count} 条预测但无法读取值")

        except PredictionModel.DoesNotExist:
            print(f"   ❌ {currency.name}: 无模型")

    # 6. 检查数据差异
    print("6. 检查预测数据差异...")

    currency_ids = list(prediction_samples.keys())
    if len(currency_ids) >= 2:
        for i in range(len(currency_ids)):
            for j in range(i + 1, len(currency_ids)):
                curr1, curr2 = currency_ids[i], currency_ids[j]
                data1, data2 = prediction_samples[curr1], prediction_samples[curr2]

                if data1["values"] == data2["values"]:
                    print(f"   ❌ {data1['name']} 和 {data2['name']} 的预测值完全相同!")
                    print(f"      值: {data1['values']}")
                else:
                    diff_pct = (
                        abs(data1["values"][0] - data2["values"][0])
                        / data1["values"][0]
                        * 100
                    )
                    print(
                        f"   ✅ {data1['name']} 和 {data2['name']} 的预测值不同 (差异: {diff_pct:.2f}%)"
                    )

    print("\n=== 修复完成 ===")


if __name__ == "__main__":
    main()
