# /backend/config/settings.py

import os
from pathlib import Path
import environ

# 初始化 django-environ
env = environ.Env(
    # 设置默认值和类型转换
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR 指向 backend/ 目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 定位到项目根目录 (crypto-insight-dashboard/) 并读取 .env 文件
# django-environ 会自动向上查找 .env 文件，但显式指定更清晰
environ.Env.read_env(os.path.join(BASE_DIR.parent, ".env"))


# --- 核心安全设置 ---

# 从 .env 文件中读取 SECRET_KEY
SECRET_KEY = env("SECRET_KEY")

# 从 .env 文件中读取 DEBUG 状态
DEBUG = env("DEBUG")

# 在生产环境中需要配置为您的域名
ALLOWED_HOSTS = []


# --- 应用定义 ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 第三方应用
    # "django_celery_beat",  # Celery Beat 调度器
    # 第三方应用
    "rest_framework",
    "corsheaders",
    "django_celery_beat",
    "djmoney",
    # 我们自己的应用 (后续创建)
    # "apps.market_data",
    "apps.market_data.apps.MarketDataConfig",
    "apps.data_ingestion.apps.DataIngestionConfig",
    "apps.api.apps.ApiConfig",  # 新增：API应用
    "apps.ml_predictions.apps.MlPredictionsConfig",
    # 'apps.users',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # 新增：CORS中间件
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # 添加模板目录
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- 数据库 ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
# 使用 dj-database-url 从 DATABASE_URL 环境变量中解析数据库配置
DATABASES = {
    "default": env.db(),
}


# --- 密码验证 ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# --- 国际化 ---
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "zh-hans"  # 设置为中文

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# --- 静态文件 (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
#
# WhiteNoise 配置
# http://whitenoise.evans.io/en/stable/django.html
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"  # <--- 添加/修改这一行
)

# --- 默认主键字段类型 ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Celery 配置 ---
# 从 .env 文件中读取 Redis 的 URL 作为 Broker
CELERY_BROKER_URL = env("REDIS_URL")
CELERY_RESULT_BACKEND = env("REDIS_URL")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# --- CORS (Cross-Origin Resource Sharing) 配置 ---
# 在开发环境中，我们允许来自本地Vue开发服务器的请求
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # 对应Vue CLI的默认端口
    "http://127.0.0.1:8080",
    "http://localhost:5173",  # 对应Vite的默认端口
    "http://127.0.0.1:5173",
]
