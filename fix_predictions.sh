#!/bin/bash
# 修复价格预测问题的脚本

echo "=== 修复加密货币价格预测问题 ==="
echo "日期: $(date)"
echo

# 1. 停止相关服务
echo "1. 停止后端服务..."
docker-compose stop backend celery_worker celery_beat

# 2. 清除Redis缓存
echo "2. 清除Redis缓存..."
docker-compose exec redis redis-cli FLUSHALL

# 3. 清除预测数据和模型文件
echo "3. 清除现有预测数据..."
docker-compose run --rm backend python manage.py shell -c "
from apps.market_data.models import PredictionModel, PricePrediction
print('删除预测数据...')
deleted_pred = PricePrediction.objects.all().delete()
print(f'删除了 {deleted_pred[0]} 条预测记录')
print('删除模型记录...')
deleted_models = PredictionModel.objects.all().delete()
print(f'删除了 {deleted_models[0]} 条模型记录')
"

# 4. 删除模型文件
echo "4. 删除模型文件..."
rm -f backend/models/*.joblib

# 5. 重新训练模型
echo "5. 重新训练所有模型..."
docker-compose run --rm backend python manage.py shell -c "
from apps.ml_predictions.tasks import train_and_predict_task
from apps.market_data.models import Currency
import time

currencies = Currency.objects.all()
print(f'开始训练 {len(currencies)} 个货币的模型')

# 首先训练比特币
try:
    bitcoin = Currency.objects.get(coingecko_id='bitcoin')
    print(f'训练比特币模型: {bitcoin.name}')
    train_and_predict_task(bitcoin.id)
    print('比特币模型训练完成')
    time.sleep(3)  # 等待数据写入
except Exception as e:
    print(f'比特币训练失败: {e}')

# 然后训练其他货币
for currency in currencies.exclude(coingecko_id='bitcoin'):
    try:
        print(f'训练模型: {currency.name}')
        train_and_predict_task(currency.id)
        print(f'{currency.name} 训练完成')
    except Exception as e:
        print(f'{currency.name} 训练失败: {e}')
"

# 6. 验证结果
echo "6. 验证训练结果..."
docker-compose run --rm backend python manage.py shell -c "
from apps.market_data.models import Currency, PredictionModel, PricePrediction

print('=== 训练结果验证 ===')
currencies = Currency.objects.all()

for currency in currencies:
    try:
        model = PredictionModel.objects.filter(
            currency=currency, is_active=True
        ).latest('version')
        pred_count = PricePrediction.objects.filter(model_run=model).count()
        
        # 获取第一个预测值作为唯一性检查
        first_pred = PricePrediction.objects.filter(model_run=model).first()
        pred_value = float(first_pred.predicted_price.amount) if first_pred else 0
        
        print(f'{currency.name}: {pred_count} 条预测, 首个预测值: {pred_value:.2f}')
    except Exception as e:
        print(f'{currency.name}: 无模型 - {e}')
"

# 7. 重新启动服务
echo "7. 重新启动服务..."
docker-compose up -d backend celery_worker celery_beat

echo
echo "=== 修复完成 ==="
echo "请访问前端页面验证不同货币是否显示不同的预测结果"
