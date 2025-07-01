from django.core.management.base import BaseCommand
from apps.data_ingestion.tasks import dispatch_market_data_updates
from apps.ml_predictions.tasks import run_all_pipelines_task
import time


class Command(BaseCommand):
    help = "运行完整的数据获取和ML训练流程"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fetch-only",
            action="store_true",
            help="只获取数据，不运行ML训练",
        )
        parser.add_argument(
            "--train-only",
            action="store_true",
            help="只运行ML训练，不获取新数据",
        )
        parser.add_argument(
            "--wait-time",
            type=int,
            default=300,
            help="数据获取和训练之间的等待时间（秒，默认300秒）",
        )

    def handle(self, *args, **options):
        """运行完整的数据获取和训练流程"""

        fetch_only = options["fetch_only"]
        train_only = options["train_only"]
        wait_time = options["wait_time"]

        if train_only:
            self.stdout.write(self.style.SUCCESS("🚀 开始运行ML训练流程..."))
            run_all_pipelines_task.delay()
            self.stdout.write(self.style.SUCCESS("✅ ML训练任务已派发"))
            return

        if not train_only:
            self.stdout.write(self.style.SUCCESS("📊 开始获取市场数据..."))
            dispatch_market_data_updates.delay()
            self.stdout.write(self.style.SUCCESS("✅ 数据获取任务已派发"))

        if fetch_only:
            return

        # 等待数据获取完成
        self.stdout.write(
            self.style.WARNING(f"⏳ 等待 {wait_time} 秒让数据获取完成...")
        )
        time.sleep(wait_time)

        # 运行ML训练
        self.stdout.write(self.style.SUCCESS("🚀 开始运行ML训练流程..."))
        run_all_pipelines_task.delay()
        self.stdout.write(self.style.SUCCESS("✅ ML训练任务已派发"))

        self.stdout.write(
            self.style.SUCCESS(
                "\n🎉 完整的数据获取和训练流程已启动！\n"
                "📝 你可以通过以下方式监控任务进度:\n"
                "   • 查看Docker logs: docker-compose logs -f crypto_celery_worker\n"
                "   • 查看Django logs: docker-compose logs -f crypto_backend"
            )
        )
