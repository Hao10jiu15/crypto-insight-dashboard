from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.market_data.models import Currency, PredictionModel, PricePrediction
from apps.ml_predictions.tasks import train_and_predict_task
import time


class Command(BaseCommand):
    help = "清除缓存，重新训练模型并生成预测数据"

    def add_arguments(self, parser):
        parser.add_argument(
            "--currency",
            type=str,
            help="指定货币的coingecko_id，不指定则处理所有货币",
        )
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="清除所有预测相关的缓存",
        )
        parser.add_argument(
            "--clear-data",
            action="store_true",
            help="清除所有预测数据重新开始",
        )

    def handle(self, *args, **options):
        if options["clear_cache"]:
            self.stdout.write("清除缓存...")
            # 清除所有与预测相关的缓存
            cache.delete_many(
                [
                    key
                    for key in cache._cache.keys()
                    if "forecast" in key or "prediction" in key
                ]
            )
            self.stdout.write(self.style.SUCCESS("✅ 缓存已清除"))

        if options["clear_data"]:
            self.stdout.write("清除现有预测数据...")
            PricePrediction.objects.all().delete()
            PredictionModel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ 预测数据已清除"))

        # 获取要处理的货币
        if options["currency"]:
            try:
                currencies = [Currency.objects.get(coingecko_id=options["currency"])]
            except Currency.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ 未找到货币: {options["currency"]}')
                )
                return
        else:
            currencies = Currency.objects.all()

        self.stdout.write(f"开始处理 {len(currencies)} 个货币的预测...")

        # 先处理比特币
        bitcoin_currency = None
        other_currencies = []

        for currency in currencies:
            if currency.coingecko_id == "bitcoin":
                bitcoin_currency = currency
            else:
                other_currencies.append(currency)

        # 首先训练比特币模型
        if bitcoin_currency:
            self.stdout.write(f"训练比特币模型: {bitcoin_currency.name}")
            try:
                train_and_predict_task(bitcoin_currency.id)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {bitcoin_currency.name} 训练完成")
                )
                time.sleep(2)  # 确保数据写入完成
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {bitcoin_currency.name} 训练失败: {e}")
                )

        # 然后训练其他货币模型
        for currency in other_currencies:
            self.stdout.write(f"训练模型: {currency.name}")
            try:
                train_and_predict_task(currency.id)
                self.stdout.write(self.style.SUCCESS(f"✅ {currency.name} 训练完成"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {currency.name} 训练失败: {e}"))

        # 显示最终统计
        self.stdout.write("\n=== 最终统计 ===")
        for currency in currencies:
            try:
                model = PredictionModel.objects.get(currency=currency, is_active=True)
                pred_count = PricePrediction.objects.filter(model_run=model).count()
                self.stdout.write(f"{currency.name}: {pred_count} 条预测记录")
            except PredictionModel.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"{currency.name}: 无模型"))

        self.stdout.write(self.style.SUCCESS("\n🎉 所有处理完成"))
