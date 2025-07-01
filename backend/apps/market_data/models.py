# /backend/apps/market_data/models.py
from django.db import models
from djmoney.models.fields import MoneyField


class Currency(models.Model):
    """
    存储每种加密货币的静态信息。
    """

    coingecko_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="CoinGecko API 使用的唯一ID",
    )  #
    symbol = models.CharField(max_length=20, help_text="货币符号，如 'btc'")  #
    name = models.CharField(max_length=100, help_text="货币全名，如 'Bitcoin'")  #

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ["id"]

    def __str__(self):
        return self.name


class PredictionModel(models.Model):
    """
    存储我们训练的机器学习模型元数据。
    """

    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="prediction_models"
    )  #
    model_file_path = models.CharField(max_length=255)  #
    version = models.IntegerField()  #
    trained_at = models.DateTimeField(auto_now_add=True)  #
    metrics = models.JSONField(default=dict)  #
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("currency", "version")
        ordering = ["-trained_at"]

    def __str__(self):
        return f"{self.currency.name} - v{self.version}"


class MarketData(models.Model):
    """
    存储历史OHLCV数据的TimescaleDB超表。
    """

    time = models.DateTimeField(
        db_index=True, help_text="数据点的时间戳，超表的时间维度"
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="market_data"
    )
    open = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    high = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    low = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    close = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    volume = models.DecimalField(max_digits=30, decimal_places=8)
    source = models.CharField(max_length=50, default="CoinGecko")

    # --- 技术指标字段 ---
    ma_7d = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    ma_30d = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    rsi = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    macd_line = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    macd_signal = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )
    macd_hist = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )

    class Meta:
        unique_together = ("time", "currency")
        ordering = ["-time"]

    def __str__(self):
        return f"{self.currency.name} at {self.time}"

class PricePrediction(models.Model):
    """
    存储模型预测结果的TimescaleDB超表。
    """

    time = models.DateTimeField(
        db_index=True, help_text="预测对应的时间戳，超表时间维度"
    )
    predicted_price = MoneyField(
        max_digits=19,
        decimal_places=4,
        default_currency="USD",
        help_text="预测值 (yhat)",
    )
    prediction_lower_bound = MoneyField(
        max_digits=19,
        decimal_places=4,
        default_currency="USD",
        null=True,
        help_text="预测置信下界 (yhat_lower)",
    )
    prediction_upper_bound = MoneyField(
        max_digits=19,
        decimal_places=4,
        default_currency="USD",
        null=True,
        help_text="预测置信上界 (yhat_upper)",
    )
    model_run = models.ForeignKey(
        PredictionModel, on_delete=models.CASCADE, related_name="predictions"
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="predictions"
    )

    class Meta:
        unique_together = ("time", "model_run", "currency")
        ordering = ["-time"]

    def __str__(self):
        return f"Prediction for {self.currency.name} at {self.time}"
