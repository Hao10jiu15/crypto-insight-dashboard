# # /backend/apps/api/views.py

from django.shortcuts import render
from datetime import datetime
from django.utils import timezone
from django.core.cache import cache
import requests

# --- Django REST Framework Imports ---
# 修正：同时导入 generics 和 viewsets
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

# --- Database Function and Model Imports ---
from django.db.models import Min, Max, Sum, F
from .db_functions import TimeBucket, First, Last
from apps.market_data.models import (
    MarketData,
    Currency,
    PredictionModel,
    PricePrediction,
)

import joblib
import pandas as pd

# --- Serializer Imports ---
from .serializers import CurrencySerializer, PricePredictionSerializer

# --- 视图类定义 ---


class CurrencyListView(generics.ListAPIView):
    """
    一个只读API视图，用于提供所有加密货币的列表。
    """

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class MarketDataViewSet(viewsets.ViewSet):
    """
    一个用于获取历史市场数据的ViewSet (已修正)。
    """

    def list(self, request, *args, **kwargs):
        currency_coingecko_id = request.query_params.get("currency_id")
        if not currency_coingecko_id:
            raise ParseError("查询参数 'currency_id' 是必需的。")

        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        queryset = MarketData.objects.filter(
            currency__coingecko_id=currency_coingecko_id
        ).order_by("time")

        if start_date_str:
            naive_start_date = datetime.fromisoformat(start_date_str)
            aware_start_date = timezone.make_aware(naive_start_date)
            queryset = queryset.filter(time__gte=aware_start_date)
        if end_date_str:
            naive_end_date = datetime.fromisoformat(end_date_str)
            aware_end_date = timezone.make_aware(naive_end_date)
            queryset = queryset.filter(time__lte=aware_end_date)

        # 注意：此版本为了提供技术指标，暂时不进行interval聚合
        # 直接返回日线数据

        # 5. 格式化结果
        formatted_data = []
        for item in queryset:
            timestamp = int(item.time.timestamp() * 1000)
            formatted_data.append(
                [
                    timestamp,
                    # 【修正】通过 .amount 属性获取MoneyField的数值
                    float(item.open.amount),
                    float(item.close.amount),
                    float(item.low.amount),
                    float(item.high.amount),
                    float(item.volume or 0),
                    float(item.ma_7d) if item.ma_7d is not None else None,
                    float(item.ma_30d) if item.ma_30d is not None else None,
                    float(item.rsi) if item.rsi is not None else None,
                    float(item.macd_line) if item.macd_line is not None else None,
                    float(item.macd_signal) if item.macd_signal is not None else None,
                    float(item.macd_hist) if item.macd_hist is not None else None,
                ]
            )

        return Response({"data": formatted_data})


class CurrencyMetricsView(viewsets.ViewSet):
    """
    提供单个货币的最新市场指标。
    """

    def retrieve(self, request, pk=None):
        currency_coingecko_id = pk
        cache_key = f"metrics_{currency_coingecko_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": currency_coingecko_id,
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                return Response({"error": "未找到该货币的数据"}, status=404)

            metrics = data[0]
            formatted_data = {
                "current_price": metrics.get("current_price"),
                "market_cap": metrics.get("market_cap"),
                "volume_24h": metrics.get("total_volume"),  # 添加24小时交易量
                "high_24h": metrics.get("high_24h"),
                "low_24h": metrics.get("low_24h"),
                "price_change_percentage_24h": metrics.get(
                    "price_change_percentage_24h"
                ),
                "last_updated": metrics.get("last_updated"),
            }

            cache.set(cache_key, formatted_data, 60)

            return Response(formatted_data)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"请求外部API失败: {e}"}, status=502)


class MarketShareView(viewsets.ViewSet):
    """
    提供市值排名前10的加密货币数据，用于饼图。
    """

    def list(self, request):
        cache_key = "market_share_top10"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            formatted_data = [
                {"value": item.get("market_cap"), "name": item.get("name")}
                for item in data
            ]

            cache.set(cache_key, formatted_data, 300)
            return Response(formatted_data)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"请求外部API失败: {e}"}, status=502)


class ForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    提供指定货币的最新价格预测数据。
    """

    serializer_class = PricePredictionSerializer

    def get_queryset(self):
        currency_id = self.request.query_params.get("currency_id")
        include_historical = (
            self.request.query_params.get("include_historical", "false").lower()
            == "true"
        )

        if not currency_id:
            return PricePrediction.objects.none()

        try:
            latest_run = PredictionModel.objects.filter(
                currency__coingecko_id=currency_id, is_active=True
            ).latest("version")
        except PredictionModel.DoesNotExist:
            # 如果没有找到模型，直接返回空查询集
            return PricePrediction.objects.none()

        # 根据参数决定返回的数据范围
        if include_historical:
            # 返回完整的预测数据（历史拟合+未来预测）
            print(f"🔍 DEBUG: {currency_id} 请求完整预测数据")
            return PricePrediction.objects.filter(model_run=latest_run).order_by("time")
        else:
            # 只返回未来3天的预测数据
            print(f"🔍 DEBUG: {currency_id} 请求未来预测数据")
            return PricePrediction.objects.filter(
                model_run=latest_run, time__gt=timezone.now()
            ).order_by("time")

    def list(self, request, *args, **kwargs):
        """重写list方法以添加缓存控制和调试信息"""
        currency_id = request.query_params.get("currency_id")
        include_historical = (
            request.query_params.get("include_historical", "false").lower() == "true"
        )

        if not currency_id:
            return Response({"error": "缺少currency_id参数"}, status=400)

        print(
            f"🔍 DEBUG: 请求 {currency_id} 的预测数据 (包含历史: {include_historical})"
        )

        # 检查货币是否存在
        try:
            currency = Currency.objects.get(coingecko_id=currency_id)
        except Currency.DoesNotExist:
            return Response({"error": f"未找到货币: {currency_id}"}, status=404)

        # 检查是否存在该货币的模型
        try:
            latest_run = PredictionModel.objects.filter(
                currency__coingecko_id=currency_id, is_active=True
            ).latest("version")
            print(
                f"🔍 DEBUG: 找到模型 - 货币: {latest_run.currency.name}, 版本: {latest_run.version}, 文件: {latest_run.model_file_path}"
            )

            # 检查预测数据数量
            pred_count = PricePrediction.objects.filter(model_run=latest_run).count()
            print(f"🔍 DEBUG: 该模型有 {pred_count} 条预测记录")

        except PredictionModel.DoesNotExist:
            print(f"🔍 DEBUG: 未找到 {currency_id} 的模型")
            return Response({"error": f"未找到 {currency_id} 的预测模型"}, status=404)

        # 使用更具体的缓存键，包含模型版本和历史数据参数
        historical_suffix = "_with_hist" if include_historical else "_future_only"
        try:
            latest_run = PredictionModel.objects.filter(
                currency__coingecko_id=currency_id, is_active=True
            ).latest("version")
            cache_key = f"forecast_data_{currency_id}_v{latest_run.version}{historical_suffix}_{timezone.now().strftime('%Y%m%d_%H')}"
        except PredictionModel.DoesNotExist:
            cache_key = f"forecast_data_{currency_id}_nomodel{historical_suffix}_{timezone.now().strftime('%Y%m%d_%H')}"

        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"🔍 DEBUG: 返回缓存数据")
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        print(
            f"🔍 DEBUG: 生成新数据，响应状态: {response.status_code}, 数据长度: {len(response.data) if response.data else 0}"
        )

        # 缓存1小时
        if response.status_code == 200:
            cache.set(cache_key, response.data, 3600)

        return response


class ForecastComponentsView(viewsets.ViewSet):
    """
    提供预测模型的组件图数据 (趋势, 周季节性, 外部特征影响等)。
    """

    def list(self, request):
        currency_id = request.query_params.get("currency_id")
        if not currency_id:
            raise ParseError("查询参数 'currency_id' 是必需的。")

        # 使用更具体的缓存键，包含货币ID、模型版本和时间戳
        try:
            model_record = PredictionModel.objects.filter(
                currency__coingecko_id=currency_id, is_active=True
            ).latest("version")
            cache_key = f"forecast_components_{currency_id}_v{model_record.version}_{timezone.now().strftime('%Y%m%d_%H')}"
        except PredictionModel.DoesNotExist:
            return Response({"error": "未找到该货币的训练模型"}, status=404)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        try:
            # 1. 加载指定货币的最新模型 (已在上面获取)
            model = joblib.load(model_record.model_file_path)

            # 2. 获取该货币的历史数据用于预测
            currency = model_record.currency
            historical_data = (
                MarketData.objects.filter(currency=currency)
                .order_by("time")
                .values("time", "close")
            )

            if len(historical_data) < 30:
                return Response({"error": "历史数据不足"}, status=400)

            # 准备历史数据DataFrame
            df = pd.DataFrame(list(historical_data))
            df.rename(columns={"time": "ds", "close": "y"}, inplace=True)
            df["ds"] = df["ds"].dt.tz_localize(None)

            # 为多变量模型准备比特币特征数据
            if "btc_price" in model.extra_regressors and currency_id != "bitcoin":
                btc_hist_data = (
                    MarketData.objects.filter(currency__coingecko_id="bitcoin")
                    .order_by("time")
                    .values("time", "close")
                )
                df_btc_hist = pd.DataFrame(list(btc_hist_data))
                df_btc_hist.rename(
                    columns={"time": "ds", "close": "btc_price"}, inplace=True
                )
                df_btc_hist["ds"] = df_btc_hist["ds"].dt.tz_localize(None)

                df = pd.merge(df, df_btc_hist, on="ds", how="left").dropna()

            # 创建未来数据帧（预测未来3天）
            future_df = model.make_future_dataframe(periods=3)

            # 为未来预测添加比特币特征
            if "btc_price" in model.extra_regressors and currency_id != "bitcoin":
                try:
                    btc_model_record = PredictionModel.objects.filter(
                        currency__coingecko_id="bitcoin", is_active=True
                    ).latest("version")
                    btc_predictions = PricePrediction.objects.filter(
                        model_run=btc_model_record
                    ).values("time", "predicted_price")

                    df_btc_pred = pd.DataFrame(list(btc_predictions))
                    df_btc_pred.rename(
                        columns={"time": "ds", "predicted_price": "btc_price"},
                        inplace=True,
                    )
                    df_btc_pred["ds"] = df_btc_pred["ds"].dt.tz_localize(None)

                    future_df = pd.merge(future_df, df_btc_pred, on="ds", how="left")
                    future_df["btc_price"] = future_df["btc_price"].fillna(
                        method="ffill"
                    )
                except Exception as e:
                    print(f"添加比特币特征到未来数据失败: {e}")
                    return Response({"error": "无法获取比特币预测数据"}, status=500)

            forecast = model.predict(future_df)

            # 2. 生成组件图的figure对象
            fig = model.plot_components(forecast)

            # 3. 从figure对象中提取数据
            components_data = {}
            for i, ax in enumerate(fig.axes):
                component_name = ax.get_title()
                if not component_name:
                    continue

                # 提取线条数据 (预测值)
                line = ax.lines[0]
                dates = [d.strftime("%Y-%m-%d") for d in line.get_xdata()]
                values = line.get_ydata().tolist()

                # 提取置信区间数据 (填充区域)
                collection = ax.collections[0]
                path = collection.get_paths()[0]
                vertices = path.vertices
                lower_bound = vertices[: len(values), 1].tolist()
                upper_bound = vertices[len(values) :, 1][::-1].tolist()

                components_data[component_name] = {
                    "dates": dates,
                    "values": values,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                }

            # 缓存结果1小时
            cache.set(cache_key, components_data, 3600)

            return Response(components_data)

        except PredictionModel.DoesNotExist:
            return Response({"error": "未找到该货币的训练模型"}, status=404)
        except Exception as e:
            return Response({"error": f"生成组件数据时出错: {e}"}, status=500)
