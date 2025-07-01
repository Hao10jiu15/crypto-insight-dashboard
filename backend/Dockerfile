# # --- 阶段一：构建阶段 (Builder Stage) ---
# FROM python:3.11 as builder

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# RUN apt-get update && apt-get install -y build-essential

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt


# # --- 阶段二：最终阶段 (Final Stage) ---
# FROM python:3.11-slim

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# WORKDIR /app

# # 从构建阶段拷贝已经安装好的Python库
# COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# # 【修正】从构建阶段拷贝由pip安装的可执行文件
# COPY --from=builder /usr/local/bin /usr/local/bin

# # 复制我们自己的应用代码
# COPY . .

# --- 阶段一：构建阶段 (Builder Stage) ---
FROM python:3.11 as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

# **新增：升级 pip 到最新版本**
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
# 移除 --resume-retries，因为它不被当前 pip 版本识别或用法不正确
# 保留 --default-timeout 和 --retries 来改善下载稳定性
RUN pip install --no-cache-dir --default-timeout=600 --retries=5 -r requirements.txt

# --- 阶段二：最终阶段 (Final Stage) ---
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 从构建阶段拷贝已经安装好的Python库
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 【修正】从构建阶段拷贝由pip安装的可执行文件
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制我们自己的应用代码
COPY . .