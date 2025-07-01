# /backend/apps/market_data/admin.py
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.html import format_html
from .models import Currency, PredictionModel, MarketData, PricePrediction


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """
    自定义 Currency 模型在Admin后台的显示。
    """

    list_display = (
        "id",
        "name",
        "symbol",
        "coingecko_id",
        "data_count",
        "model_status",
        "action_buttons",
    )
    search_fields = ("name", "symbol", "coingecko_id")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "add-default-currencies/",
                self.add_default_currencies,
                name="add_default_currencies",
            ),
            path(
                "fetch-data/<int:currency_id>/",
                self.fetch_data,
                name="fetch_currency_data",
            ),
            path(
                "train-model/<int:currency_id>/",
                self.train_model,
                name="train_currency_model",
            ),
            path(
                "full-pipeline/<int:currency_id>/",
                self.full_pipeline,
                name="full_currency_pipeline",
            ),
            path("bulk-operations/", self.bulk_operations, name="bulk_operations"),
        ]
        return custom_urls + urls

    def data_count(self, obj):
        """显示该货币的数据量"""
        count = MarketData.objects.filter(currency=obj).count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} 条</span>', count
            )
        else:
            return format_html('<span style="color: red;">无数据</span>')

    data_count.short_description = "数据量"

    def model_status(self, obj):
        """显示该货币的模型状态"""
        try:
            model = PredictionModel.objects.filter(currency=obj, is_active=True).latest(
                "version"
            )
            predictions_count = PricePrediction.objects.filter(model_run=model).count()
            return format_html(
                '<span style="color: blue; font-weight: bold;">v{} ({} 条预测)</span>',
                model.version,
                predictions_count,
            )
        except PredictionModel.DoesNotExist:
            return format_html('<span style="color: orange;">未训练</span>')

    model_status.short_description = "模型状态"

    def action_buttons(self, obj):
        """显示操作按钮"""
        return format_html(
            '<a class="button" href="fetch-data/{}/" style="margin-right: 5px;">📊 获取数据</a>'
            '<a class="button" href="train-model/{}/" style="margin-right: 5px;">🚀 训练模型</a>'
            '<a class="button" href="full-pipeline/{}/">⚡ 完整流程</a>',
            obj.pk,
            obj.pk,
            obj.pk,
        )

    action_buttons.short_description = "操作"
    action_buttons.allow_tags = True

    def changelist_view(self, request, extra_context=None):
        """自定义列表视图，添加批量操作按钮"""
        extra_context = extra_context or {}
        extra_context["custom_buttons"] = [
            {
                "url": "add-default-currencies/",
                "title": "🆕 添加默认货币",
                "class": "default",
            },
            {"url": "bulk-operations/", "title": "🔄 批量操作", "class": "default"},
        ]
        return super().changelist_view(request, extra_context)

    def add_default_currencies(self, request):
        """添加默认货币"""
        if request.method == "POST":
            try:
                default_currencies = [
                    {"name": "Bitcoin", "symbol": "BTC", "coingecko_id": "bitcoin"},
                    {"name": "Ethereum", "symbol": "ETH", "coingecko_id": "ethereum"},
                    {"name": "Tether", "symbol": "USDT", "coingecko_id": "tether"},
                    {"name": "BNB", "symbol": "BNB", "coingecko_id": "binancecoin"},
                    {"name": "Solana", "symbol": "SOL", "coingecko_id": "solana"},
                    {"name": "XRP", "symbol": "XRP", "coingecko_id": "ripple"},
                    {"name": "Cardano", "symbol": "ADA", "coingecko_id": "cardano"},
                ]

                created_count = 0
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

                messages.success(request, f"成功添加了 {created_count} 个新货币！")
                return redirect("../")

            except Exception as e:
                messages.error(request, f"添加货币时出错: {str(e)}")
                return redirect("../")

        return render(
            request,
            "admin/currency/add_default.html",
            {
                "title": "添加默认货币",
                "opts": self.model._meta,
            },
        )

    def fetch_data(self, request, currency_id):
        """获取单个货币的数据"""
        try:
            currency = Currency.objects.get(id=currency_id)
            from apps.data_ingestion.tasks import fetch_historical_data_for_coin

            task = fetch_historical_data_for_coin.delay(currency_id)
            messages.success(
                request, f"正在为 {currency.name} 获取数据，任务ID: {task.id}"
            )

        except Currency.DoesNotExist:
            messages.error(request, "货币不存在")
        except Exception as e:
            messages.error(request, f"启动数据获取任务时出错: {str(e)}")

        return redirect("../../../")

    def train_model(self, request, currency_id):
        """训练单个货币的模型"""
        try:
            currency = Currency.objects.get(id=currency_id)
            from apps.ml_predictions.tasks import train_and_predict_task

            task = train_and_predict_task.delay(currency_id)
            messages.success(
                request, f"正在为 {currency.name} 训练模型，任务ID: {task.id}"
            )

        except Currency.DoesNotExist:
            messages.error(request, "货币不存在")
        except Exception as e:
            messages.error(request, f"启动训练任务时出错: {str(e)}")

        return redirect("../../../")

    def full_pipeline(self, request, currency_id):
        """运行完整流程"""
        try:
            currency = Currency.objects.get(id=currency_id)
            from apps.ml_predictions.tasks import full_pipeline_for_new_currency

            task = full_pipeline_for_new_currency.delay(currency.coingecko_id)
            messages.success(
                request, f"正在为 {currency.name} 运行完整流程，任务ID: {task.id}"
            )

        except Currency.DoesNotExist:
            messages.error(request, "货币不存在")
        except Exception as e:
            messages.error(request, f"启动完整流程时出错: {str(e)}")

        return redirect("../../../")

    def bulk_operations(self, request):
        """批量操作页面"""
        if request.method == "POST":
            operation = request.POST.get("operation")

            try:
                if operation == "fetch_all_data":
                    from apps.data_ingestion.tasks import dispatch_market_data_updates

                    task = dispatch_market_data_updates.delay()
                    messages.success(
                        request, f"正在为所有货币获取数据，任务ID: {task.id}"
                    )

                elif operation == "train_all_models":
                    from apps.ml_predictions.tasks import run_all_pipelines_task

                    task = run_all_pipelines_task.delay()
                    messages.success(request, f"正在训练所有模型，任务ID: {task.id}")

                elif operation == "full_pipeline_all":
                    from apps.data_ingestion.tasks import dispatch_market_data_updates
                    from apps.ml_predictions.tasks import run_all_pipelines_task

                    # 先获取数据
                    data_task = dispatch_market_data_updates.delay()
                    messages.info(request, f"数据获取任务已启动: {data_task.id}")

                    # 延迟5分钟后启动训练
                    train_task = run_all_pipelines_task.apply_async(countdown=300)
                    messages.success(
                        request, f"训练任务将在5分钟后开始: {train_task.id}"
                    )

                else:
                    messages.error(request, "未知操作")

            except Exception as e:
                messages.error(request, f"执行批量操作时出错: {str(e)}")

            return redirect("../")

        return render(
            request,
            "admin/currency/bulk_operations.html",
            {
                "title": "批量操作",
                "opts": self.model._meta,
            },
        )


@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    """
    自定义 PredictionModel 模型在Admin后台的显示。
    """

    list_display = (
        "id",
        "currency",
        "version",
        "trained_at",
        "is_active",
        "predictions_count",
    )
    search_fields = ("currency__name",)
    list_filter = ("currency", "is_active")

    def predictions_count(self, obj):
        """显示该模型的预测数量"""
        count = PricePrediction.objects.filter(model_run=obj).count()
        return format_html('<span style="font-weight: bold;">{} 条</span>', count)

    predictions_count.short_description = "预测数量"


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    """
    自定义 MarketData 模型在Admin后台的显示。
    """

    list_display = ("id", "currency", "time", "open", "high", "low", "close", "volume")
    search_fields = ("currency__name",)
    list_filter = ("currency",)
    date_hierarchy = "time"  # 添加日期层级筛选


@admin.register(PricePrediction)
class PricePredictionAdmin(admin.ModelAdmin):
    """
    自定义 PricePrediction 模型在Admin后台的显示。
    """

    list_display = ("id", "currency", "time", "predicted_price", "model_run")
    search_fields = ("currency__name",)
    list_filter = ("currency",)
    date_hierarchy = "time"
