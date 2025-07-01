from django.core.management.base import BaseCommand
from apps.market_data.models import Currency


class Command(BaseCommand):
    help = "初始化默认的加密货币数据"

    def handle(self, *args, **options):
        """初始化默认的加密货币"""

        default_currencies = [
            {
                "name": "Bitcoin",
                "symbol": "BTC",
                "coingecko_id": "bitcoin",
            },
            {
                "name": "Ethereum",
                "symbol": "ETH",
                "coingecko_id": "ethereum",
            },
            {
                "name": "Tether",
                "symbol": "USDT",
                "coingecko_id": "tether",
            },
            {
                "name": "BNB",
                "symbol": "BNB",
                "coingecko_id": "binancecoin",
            },
            {
                "name": "Solana",
                "symbol": "SOL",
                "coingecko_id": "solana",
            },
            {
                "name": "XRP",
                "symbol": "XRP",
                "coingecko_id": "ripple",
            },
        ]

        created_count = 0
        updated_count = 0

        for currency_data in default_currencies:
            currency, created = Currency.objects.get_or_create(
                coingecko_id=currency_data["coingecko_id"],
                defaults={
                    "name": currency_data["name"],
                    "symbol": currency_data["symbol"],
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ 创建新货币: {currency.name} ({currency.symbol})"
                    )
                )
            else:
                # 更新现有货币信息
                currency.name = currency_data["name"]
                currency.symbol = currency_data["symbol"]
                currency.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"🔄 更新现有货币: {currency.name} ({currency.symbol})"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n📈 初始化完成！创建了 {created_count} 个新货币，更新了 {updated_count} 个现有货币。"
            )
        )

        # 显示当前所有货币
        all_currencies = Currency.objects.all()
        self.stdout.write("\n当前数据库中的所有货币:")
        for currency in all_currencies:
            self.stdout.write(
                f"  • {currency.name} ({currency.symbol}) - {currency.coingecko_id}"
            )
