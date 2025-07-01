import os
from celery import Celery
from celery.schedules import crontab

# 为 'celery' 程序设置默认的 Django settings 模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 创建 Celery 应用实例
# 'config' 是我们Django项目的名称
app = Celery("config")

# 使用字符串'django.conf:settings'，worker就不需要为了获取配置对象而序列化它。
# namespace='CELERY' 意味着所有Celery相关的配置键在settings.py中都必须以 'CELERY_' 为前缀。
app.config_from_object("django.conf:settings", namespace="CELERY")

# 定期任务配置
app.conf.beat_schedule = {
    # 每天凌晨2点获取市场数据
    "fetch-market-data-daily": {
        "task": "apps.data_ingestion.tasks.dispatch_market_data_updates",
        "schedule": crontab(hour=2, minute=0),  # 每天凌晨2点
    },
    # 每天凌晨3点运行ML训练（给数据获取1小时的缓冲时间）
    "run-ml-training-daily": {
        "task": "apps.ml_predictions.tasks.run_all_pipelines_task",
        "schedule": crontab(hour=3, minute=0),  # 每天凌晨3点
    },
    # 每8小时更新一次数据（可选，用于更频繁的数据更新）
    "fetch-market-data-frequent": {
        "task": "apps.data_ingestion.tasks.dispatch_market_data_updates",
        "schedule": crontab(minute=0, hour="*/8"),  # 每8小时
    },
}

# 时区设置
app.conf.timezone = "UTC"

# 自动从所有已注册的Django app中加载任务模块。
app.autodiscover_tasks()
