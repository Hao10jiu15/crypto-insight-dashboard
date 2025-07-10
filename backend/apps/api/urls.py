from django.urls import path

from .views import (
    CurrencyListView,
    MarketDataViewSet,
    CurrencyMetricsView,
    MarketShareView,
    ForecastViewSet,
    ForecastComponentsView,
)

app_name = "api"

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
