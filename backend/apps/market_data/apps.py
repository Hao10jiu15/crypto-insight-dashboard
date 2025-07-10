from django.apps import AppConfig


class MarketDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.market_data"

    # 在应用就绪时导入并连接信号
    def ready(self):
        import apps.market_data.signals
