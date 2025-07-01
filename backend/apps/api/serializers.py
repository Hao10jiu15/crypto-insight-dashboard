from rest_framework import serializers
from apps.market_data.models import Currency
from djmoney.money import Money
from apps.market_data.models import PricePrediction

# from rest_framework.utils.representation import to_representation
# from .models import MarketData

class CurrencySerializer(serializers.ModelSerializer):
    """
    用于 Currency 模型的序列化器。
    """

    class Meta:
        model = Currency
        # 定义需要暴露给API的字段
        fields = ["id", "name", "symbol", "coingecko_id"]


class MarketDataSerializer(serializers.ListSerializer):
    """
    为ECharts优化的自定义序列化器。
    将MarketData查询集直接序列化为数组的数组。
    """

    def to_representation(self, data):
        # 将Money对象转换为Decimal，然后转为float
        def get_float(money_obj):
            if isinstance(money_obj, Money):
                return float(money_obj.amount)
            return float(money_obj)

        result = []
        for item in data:
            # 将时间转换为毫秒级时间戳
            timestamp = int(item.time.timestamp() * 1000)
            result.append(
                [
                    timestamp,
                    get_float(item.open),
                    get_float(item.close),
                    get_float(item.low),
                    get_float(item.high),
                ]
            )
        return result


class PricePredictionSerializer(serializers.ModelSerializer):
    """
    用于 PricePrediction 模型的序列化器。
    """

    class Meta:
        model = PricePrediction
        # 定义需要暴露给API的字段
        fields = [
            "time",
            "predicted_price",
            "prediction_lower_bound",
            "prediction_upper_bound",
        ]
