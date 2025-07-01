import os
import pandas as pd
from celery import shared_task, chain
from datetime import datetime, timezone as dt_timezone
import joblib
from prophet import Prophet
import time

from django.conf import settings
from django.utils import timezone
from django.db import transaction

from apps.market_data.models import (
    MarketData,
    Currency,
    PredictionModel,
    PricePrediction,
)

MODELS_DIR = os.path.join(settings.BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)
BITCOIN_GECKO_ID = "bitcoin"


@shared_task
def train_and_predict_task(currency_id, periods=3, max_attempts=3):
    """
    【全新单体任务】
    为一个指定的货币完成完整的"训练-预测"流程。
    预测未来3天的价格趋势。
    """
    try:
        currency = Currency.objects.get(id=currency_id)
        print(f"--- [START] 开始为 {currency.name} 处理训练和预测 ---")

        # 1. 获取数据
        data = (
            MarketData.objects.filter(currency=currency)
            .order_by("time")
            .values("time", "close")
        )
        if len(data) < 50:
            print(f"数据不足，跳过 {currency.name}。")
            return

        df = pd.DataFrame(list(data))
        df.rename(columns={"time": "ds", "close": "y"}, inplace=True)
        df["ds"] = df["ds"].dt.tz_localize(None)

        # 2. 训练模型
        model = Prophet(daily_seasonality=False)

        # 2.1 如果是山寨币，添加外部特征
        if currency.coingecko_id != BITCOIN_GECKO_ID:
            try:
                # 从数据库查询比特币的历史价格作为训练特征
                btc_hist_data = MarketData.objects.filter(
                    currency__coingecko_id=BITCOIN_GECKO_ID
                ).values("time", "close")
                df_btc_hist = pd.DataFrame(list(btc_hist_data))
                df_btc_hist.rename(
                    columns={"time": "ds", "close": "btc_price"}, inplace=True
                )
                df_btc_hist["ds"] = df_btc_hist["ds"].dt.tz_localize(None)

                df = pd.merge(df, df_btc_hist, on="ds", how="left").dropna()
                model.add_regressor("btc_price")
                print(f"✅ 已为 {currency.name} 添加比特币历史价格作为训练特征。")
            except Exception as e:
                print(f"🛑 添加比特币特征失败: {e}，将作为单变量模型训练。")

        model.fit(df)
        print(f"✅ {currency.name} 的模型训练完成。")

        # 3. 创建未来数据帧（明确指定日频率）
        future_df = model.make_future_dataframe(periods=periods, freq="D")
        print(
            f"🔍 DEBUG: {currency.name} 未来数据帧范围: {future_df['ds'].min()} 到 {future_df['ds'].max()}"
        )
        print(
            f"🔍 DEBUG: {currency.name} 历史数据最新: {df['ds'].max()}, 当前时间: {timezone.now()}"
        )

        # 3.1 如果是山寨币，为未来数据帧添加比特币特征
        if "btc_price" in model.extra_regressors:
            # 添加重试逻辑查找比特币预测数据
            attempts = 0
            while attempts < max_attempts:
                try:
                    btc_currency = Currency.objects.get(coingecko_id=BITCOIN_GECKO_ID)
                    btc_latest_run = PredictionModel.objects.filter(
                        currency=btc_currency, is_active=True
                    ).latest("version")
                    btc_predictions = PricePrediction.objects.filter(
                        model_run=btc_latest_run
                    ).values("time", "predicted_price")

                    if list(btc_predictions):
                        df_btc_pred = pd.DataFrame(list(btc_predictions))
                        df_btc_pred.rename(
                            columns={"time": "ds", "predicted_price": "btc_price"},
                            inplace=True,
                        )
                        df_btc_pred["ds"] = df_btc_pred["ds"].dt.tz_localize(None)

                        future_df = pd.merge(
                            future_df, df_btc_pred, on="ds", how="left"
                        )
                        # 使用向前填充处理缺失值
                        future_df["btc_price"] = future_df["btc_price"].ffill()
                        # 如果还有NaN，使用向后填充
                        future_df["btc_price"] = future_df["btc_price"].bfill()
                        # 如果仍然有NaN，用最后一个有效值填充
                        if future_df["btc_price"].isna().any():
                            last_valid_price = (
                                future_df["btc_price"].dropna().iloc[-1]
                                if not future_df["btc_price"].dropna().empty
                                else 50000
                            )
                            future_df["btc_price"] = future_df["btc_price"].fillna(
                                last_valid_price
                            )
                        print(
                            f"🔍 DEBUG: {currency.name} 合并后数据帧行数: {len(future_df)}"
                        )
                        print(
                            f"✅ 已为 {currency.name} 的未来数据帧添加比特币预测特征。"
                        )
                        break
                    else:
                        attempts += 1
                        if attempts < max_attempts:
                            print(
                                f"尝试 {attempts}/{max_attempts}: 比特币预测数据尚未准备好，等待10秒后重试..."
                            )
                            time.sleep(10)  # 等待10秒后重试
                        else:
                            raise ValueError(
                                f"在{max_attempts}次尝试后仍未找到比特币的预测数据"
                            )
                except Exception as e:
                    attempts += 1
                    if attempts < max_attempts:
                        print(
                            f"尝试 {attempts}/{max_attempts}: 获取比特币数据时出错: {e}，等待10秒后重试..."
                        )
                        time.sleep(10)
                    else:
                        raise ValueError(
                            f"在{max_attempts}次尝试后仍未能获取比特币预测数据: {e}"
                        )

        # 4. 生成最终预测
        final_forecast = model.predict(future_df)
        print(f"✅ {currency.name} 的价格预测已生成。")

        # 保存完整的预测数据（历史拟合+未来预测）
        print(f"🔍 DEBUG: {currency.name} 总预测数据: {len(final_forecast)} 条")
        print(
            f"🔍 DEBUG: {currency.name} 预测时间范围: {final_forecast['ds'].min()} 到 {final_forecast['ds'].max()}"
        )

        # 5. 原子化地保存所有结果
        with transaction.atomic():
            # 保存模型 - 确保每个货币有唯一的模型文件
            model_path = os.path.join(
                MODELS_DIR, f"{currency.coingecko_id}_model_v{int(time.time())}.joblib"
            )
            joblib.dump(model, model_path)
            print(f"🔍 DEBUG: {currency.name} 模型保存到: {model_path}")

            # 确保清除旧模型
            PredictionModel.objects.filter(currency=currency).update(is_active=False)
            latest_model_version = (
                PredictionModel.objects.filter(currency=currency)
                .order_by("-version")
                .first()
            )
            new_version = (
                (latest_model_version.version + 1) if latest_model_version else 1
            )

            model_record = PredictionModel.objects.create(
                currency=currency,
                model_file_path=model_path,
                version=new_version,
                is_active=True,
            )
            print(f"🔍 DEBUG: {currency.name} 模型记录创建 - 版本: {new_version}")

            # 清除该货币的旧预测数据
            deleted_count = PricePrediction.objects.filter(
                model_run__currency=currency
            ).delete()[0]
            print(f"🔍 DEBUG: {currency.name} 删除了 {deleted_count} 条旧预测记录")

            # 保存新预测数据（保存完整的预测数据）
            predictions_created = 0
            for _, row in final_forecast.iterrows():
                aware_time = timezone.make_aware(
                    row["ds"].to_pydatetime(), dt_timezone.utc
                )
                PricePrediction.objects.create(
                    currency=currency,
                    model_run=model_record,
                    time=aware_time,
                    predicted_price=row["yhat"],
                    prediction_lower_bound=row["yhat_lower"],
                    prediction_upper_bound=row["yhat_upper"],
                )
                predictions_created += 1

            print(
                f"🔍 DEBUG: {currency.name} 创建了 {predictions_created} 条新预测记录"
            )

        print(f"--- [SUCCESS] {currency.name} 的模型和预测数据已全部保存。---")

    except Exception as e:
        print(f"🛑 处理 {currency.name} 时发生严重错误: {e}")


# --- 【全新】主调度任务 ---
@shared_task
def run_all_pipelines_task():
    """
    一个主调度任务，使用适当的任务依赖执行所有货币的训练-预测工作流。
    """
    print("--- [MASTER] 启动所有货币的训练-预测主工作流 ---")

    try:
        # 1. 找到比特币
        btc = Currency.objects.get(coingecko_id=BITCOIN_GECKO_ID)
        print(f"--- 正在为 {btc.name} 派发任务 ---")

        # 2. 先处理比特币，等待任务完成
        btc_task = train_and_predict_task.apply_async(args=[btc.id])

        # 3. 获取所有山寨币
        altcoins = Currency.objects.exclude(coingecko_id=BITCOIN_GECKO_ID)

        # 4. 为每个山寨币创建依赖于比特币任务的预测任务
        for coin in altcoins:
            print(f"--- 为 {coin.name} 创建依赖于比特币的预测任务 ---")
            # 使用link参数创建任务链，确保山寨币任务仅在比特币任务成功后执行
            train_and_predict_task.apply_async(
                args=[coin.id],
                countdown=5,  # 小延迟以确保比特币数据已完全写入数据库
                link_error=handle_prediction_error.s(coin.name),
            )

        print("--- [MASTER] 所有工作流已派发完毕 ---")

    except Currency.DoesNotExist:
        print("🛑 错误：数据库中未找到比特币，无法启动ML管道。")
        return


# 添加错误处理任务
@shared_task
def handle_prediction_error(request, exc, traceback, coin_name):
    """处理预测任务失败的回调函数"""
    print(f"🛑 {coin_name} 的预测任务失败: {exc}")
    # 可以在这里添加重试逻辑或通知机制


@shared_task
def full_pipeline_for_new_currency(currency_coingecko_id):
    """
    为新创建的货币运行完整的流程：
    启动数据获取任务，完成后自动触发训练任务
    """
    from apps.data_ingestion.tasks import fetch_historical_data_for_coin
    from apps.market_data.models import Currency

    try:
        currency = Currency.objects.get(coingecko_id=currency_coingecko_id)
        print(f"--- [新货币流程] 开始为 {currency.name} 运行完整流程 ---")

        # 1. 启动数据获取任务，并在完成后链接训练任务
        fetch_task = fetch_historical_data_for_coin.apply_async(
            args=[currency.id],
            link=delayed_training_task.s(currency.id),  # 数据获取完成后自动执行训练
        )

        print(
            f"--- [新货币流程] {currency.name} 数据获取任务已启动（任务ID: {fetch_task.id}）---"
        )
        return f"Data fetch pipeline initiated for {currency.name}"

    except Currency.DoesNotExist:
        error_msg = f"🛑 未找到coingecko_id为 {currency_coingecko_id} 的货币"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"🛑 {currency_coingecko_id} 完整流程失败: {e}"
        print(error_msg)
        return error_msg


@shared_task
def delayed_training_task(fetch_result, currency_id):
    """
    延迟训练任务，在数据获取完成后执行
    """
    from apps.market_data.models import Currency
    import time

    try:
        currency = Currency.objects.get(id=currency_id)
        print(f"📊 {currency.name} 数据获取完成: {fetch_result}")
        print(f"🚀 等待5秒后开始为 {currency.name} 进行训练...")

        # 等待5秒确保数据完全写入数据库
        time.sleep(5)

        # 启动训练任务
        train_and_predict_task.delay(currency_id)

        print(f"✅ {currency.name} 训练任务已启动")
        return f"Training initiated for {currency.name}"

    except Exception as e:
        error_msg = f"🛑 延迟训练任务失败: {e}"
        print(error_msg)
        return error_msg
