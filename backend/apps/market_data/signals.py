from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Currency

# 【修正】不再在文件顶部导入任务，以打破循环依赖


@receiver(post_save, sender=Currency)
def trigger_initial_training(sender, instance, created, **kwargs):
    """
    监听Currency模型的保存信号。
    如果一个Currency实例是新创建的，则自动为它触发训练和预测任务。
    """
    if created:
        # 【修正】将导入语句移到函数内部
        from apps.ml_predictions.tasks import full_pipeline_for_new_currency

        print(
            f"检测到新货币 '{instance.name}' (ID: {instance.id}) 被创建，正在为其自动派发完整工作流..."
        )
        full_pipeline_for_new_currency.delay(instance.coingecko_id)
