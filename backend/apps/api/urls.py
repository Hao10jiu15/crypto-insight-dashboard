# /backend/apps/api/urls.py
from django.urls import path

# 确保导入了所有需要用到的视图
from .views import (
    CurrencyListView,
    MarketDataViewSet,
    CurrencyMetricsView,
    MarketShareView,
    ForecastViewSet,
    ForecastComponentsView,
)

app_name = "api"

# --- 定义最终的URL模式 ---
# 我们为每一个ViewSet的每一个动作都手动创建路径
urlpatterns = [
    # /api/currencies/
    path("currencies/", CurrencyListView.as_view(), name="currency-list"),
    # /api/market_data/
    path(
        "market_data/",
        MarketDataViewSet.as_view({"get": "list"}),
        name="marketdata-list",
    ),
    # /api/metrics/<id>/
    path(
        "metrics/<str:pk>/",
        CurrencyMetricsView.as_view({"get": "retrieve"}),
        name="metrics-detail",
    ),
    # /api/market_share/
    path(
        "market_share/",
        MarketShareView.as_view({"get": "list"}),
        name="marketshare-list",
    ),
    # /api/forecasts/
    path("forecasts/", ForecastViewSet.as_view({"get": "list"}), name="forecasts-list"),
    # /api/forecast_components/
    path(
        "forecast_components/",
        ForecastComponentsView.as_view({"get": "list"}),
        name="forecastcomponents-list",
    ),
]
