# Django 管理命令使用指南

## 概述

本项目包含多个 Django 管理命令，用于初始化货币数据、运行数据获取和 ML 训练流程。

## 可用命令

### 1. 初始化默认货币

```bash
# 在后端容器中运行
docker-compose exec crypto_backend python manage.py init_currencies
```

这个命令会：

- 创建 6 个默认的加密货币（BTC, ETH, USDT, BNB, SOL, XRP）
- 如果货币已存在，会更新其信息
- 显示创建/更新的统计信息

### 2. 运行完整数据流程

```bash
# 运行完整流程（数据获取 + ML训练）
docker-compose exec crypto_backend python manage.py run_pipeline

# 只获取数据，不训练
docker-compose exec crypto_backend python manage.py run_pipeline --fetch-only

# 只训练，不获取新数据
docker-compose exec crypto_backend python manage.py run_pipeline --train-only

# 自定义等待时间（默认300秒）
docker-compose exec crypto_backend python manage.py run_pipeline --wait-time 600
```

## 自动化流程

### 定期任务调度

系统已配置以下定期任务：

1. **每天凌晨 2 点**: 获取所有货币的市场数据
2. **每天凌晨 3 点**: 运行 ML 训练和预测
3. **每 8 小时**: 更新市场数据（可选）

### 启动 Celery Beat 调度器

```bash
# 启动定期任务调度器
docker-compose exec crypto_backend celery -A config beat --loglevel=info
```

### 新货币自动处理

当通过 Django Admin 添加新货币时，系统会自动：

1. 获取该货币的历史数据
2. 训练 ML 模型
3. 生成价格预测

## 监控任务

### 查看 Celery Worker 日志

```bash
docker-compose logs -f crypto_celery_worker
```

### 查看 Django 后端日志

```bash
docker-compose logs -f crypto_backend
```

### 检查任务状态

可以通过 Django Admin 查看：

- 货币列表: `/admin/market_data/currency/`
- 市场数据: `/admin/market_data/marketdata/`
- 预测模型: `/admin/market_data/predictionmodel/`
- 价格预测: `/admin/market_data/priceprediction/`

## 常见用法

### 首次设置

```bash
# 1. 初始化默认货币
docker-compose exec crypto_backend python manage.py init_currencies

# 2. 运行完整数据流程
docker-compose exec crypto_backend python manage.py run_pipeline

# 3. 启动定期任务调度器（在后台运行）
docker-compose exec -d crypto_backend celery -A config beat --loglevel=info
```

### 添加新货币

1. 通过 Django Admin 界面添加新货币
2. 系统会自动开始数据获取和训练流程
3. 或者手动运行：

```bash
# 为特定货币运行完整流程
docker-compose exec crypto_backend python manage.py shell -c "
from apps.ml_predictions.tasks import full_pipeline_for_new_currency
full_pipeline_for_new_currency.delay('new-coin-id')
"
```

### 手动重新训练所有模型

```bash
docker-compose exec crypto_backend python manage.py run_pipeline --train-only
```

## 注意事项

1. **API 限制**: CoinGecko API 有速率限制，建议设置适当的 API 密钥
2. **数据大小**: 训练需要足够的历史数据（至少 50 个数据点）
3. **依赖关系**: 山寨币模型依赖比特币数据，确保比特币先训练
4. **资源使用**: ML 训练可能消耗大量 CPU 和内存资源

## 故障排除

如果遇到问题：

1. 检查 Celery Worker 是否运行
2. 查看日志文件查找错误信息
3. 确认数据库连接正常
4. 验证 API 密钥配置
