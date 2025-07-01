# 修复价格预测问题的PowerShell脚本

Write-Host "=== 修复加密货币价格预测问题 ===" -ForegroundColor Green
Write-Host "日期: $(Get-Date)" -ForegroundColor Green
Write-Host ""

# 1. 停止相关服务
Write-Host "1. 停止后端服务..." -ForegroundColor Yellow
docker-compose stop backend celery_worker celery_beat

# 2. 清除Redis缓存
Write-Host "2. 清除Redis缓存..." -ForegroundColor Yellow
docker-compose exec redis redis-cli FLUSHALL

# 3. 删除模型文件
Write-Host "3. 删除模型文件..." -ForegroundColor Yellow
if (Test-Path "backend\models\*.joblib") {
    Remove-Item "backend\models\*.joblib" -Force
    Write-Host "模型文件已删除" -ForegroundColor Green
}
else {
    Write-Host "没有找到模型文件" -ForegroundColor Gray
}

# 4. 清除数据库中的预测数据
Write-Host "4. 清除数据库预测数据..." -ForegroundColor Yellow
$clearDataScript = @"
from apps.market_data.models import PredictionModel, PricePrediction
print('删除预测数据...')
deleted_pred = PricePrediction.objects.all().delete()
print(f'删除了 {deleted_pred[0]} 条预测记录')
print('删除模型记录...')
deleted_models = PredictionModel.objects.all().delete()
print(f'删除了 {deleted_models[0]} 条模型记录')
print('数据清除完成')
"@

docker-compose run --rm backend python manage.py shell -c $clearDataScript

# 5. 重新训练模型
Write-Host "5. 重新训练所有模型..." -ForegroundColor Yellow
$trainScript = @"
from apps.ml_predictions.tasks import train_and_predict_task
from apps.market_data.models import Currency
import time

currencies = Currency.objects.all()
print(f'开始训练 {len(currencies)} 个货币的模型')

# 首先训练比特币
try:
    bitcoin = Currency.objects.get(coingecko_id='bitcoin')
    print(f'正在训练比特币模型: {bitcoin.name}')
    train_and_predict_task(bitcoin.id)
    print('✅ 比特币模型训练完成')
    time.sleep(3)  # 等待数据写入
except Exception as e:
    print(f'❌ 比特币训练失败: {e}')

# 然后训练其他货币
other_currencies = currencies.exclude(coingecko_id='bitcoin')
for i, currency in enumerate(other_currencies, 1):
    try:
        print(f'正在训练模型 ({i}/{len(other_currencies)}): {currency.name}')
        train_and_predict_task(currency.id)
        print(f'✅ {currency.name} 训练完成')
        time.sleep(1)  # 短暂延迟避免资源冲突
    except Exception as e:
        print(f'❌ {currency.name} 训练失败: {e}')

print('所有模型训练完成')
"@

docker-compose run --rm backend python manage.py shell -c $trainScript

# 6. 验证结果
Write-Host "6. 验证训练结果..." -ForegroundColor Yellow
$verifyScript = @"
from apps.market_data.models import Currency, PredictionModel, PricePrediction

print('\n=== 训练结果验证 ===')
currencies = Currency.objects.all()
prediction_samples = {}

for currency in currencies:
    try:
        model = PredictionModel.objects.filter(
            currency=currency, is_active=True
        ).latest('version')
        pred_count = PricePrediction.objects.filter(model_run=model).count()
        
        # 获取前3个预测值作为唯一性检查
        predictions = PricePrediction.objects.filter(model_run=model).order_by('time')[:3]
        pred_values = [float(p.predicted_price.amount) for p in predictions]
        prediction_samples[currency.coingecko_id] = pred_values
        
        print(f'✅ {currency.name}: {pred_count} 条预测, 前3个值: {pred_values}')
    except Exception as e:
        print(f'❌ {currency.name}: 无模型 - {e}')

# 检查预测值是否相同
print('\n=== 检查预测数据唯一性 ===')
currency_ids = list(prediction_samples.keys())
if len(currency_ids) >= 2:
    same_predictions = []
    for i in range(len(currency_ids)):
        for j in range(i + 1, len(currency_ids)):
            curr1, curr2 = currency_ids[i], currency_ids[j]
            if prediction_samples[curr1] == prediction_samples[curr2]:
                same_predictions.append((curr1, curr2))
                print(f'❌ {curr1} 和 {curr2} 的预测值完全相同!')
            else:
                print(f'✅ {curr1} 和 {curr2} 的预测值不同')
    
    if not same_predictions:
        print('🎉 所有货币的预测值都是唯一的!')
    else:
        print(f'⚠️  发现 {len(same_predictions)} 对相同的预测值')
else:
    print('货币数量不足，无法比较')
"@

docker-compose run --rm backend python manage.py shell -c $verifyScript

# 7. 重新启动服务
Write-Host "7. 重新启动服务..." -ForegroundColor Yellow
docker-compose up -d backend celery_worker celery_beat

Write-Host ""
Write-Host "=== 修复完成 ===" -ForegroundColor Green
Write-Host "请访问前端页面验证不同货币是否显示不同的预测结果" -ForegroundColor Green
Write-Host "前端地址: http://localhost:3000" -ForegroundColor Cyan
