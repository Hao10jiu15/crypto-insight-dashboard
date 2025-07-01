# /backend/config/__init__.py

# 导入我们创建的Celery app实例，以确保它在Django启动时被加载
from .celery import app as celery_app

__all__ = ("celery_app",)
