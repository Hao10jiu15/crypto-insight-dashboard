# 🚀 加密货币价格预测系统

一个基于机器学习的加密货币价格预测系统，提供实时数据获取、模型训练和价格预测功能。

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ 功能特性

### 🎯 核心功能

- **🤖 机器学习预测**: 使用 Facebook Prophet 模型进行价格预测
- **📊 实时数据**: 从 CoinGecko API 获取实时市场数据
- **🔄 自动化流程**: 定时任务自动获取数据和重训练模型
- **📈 可视化图表**: 交互式价格图表和预测可视化
- **🎛️ Web 管理**: Django Admin 界面一键管理所有操作

### 📱 用户界面

- **💻 响应式设计**: 支持桌面和移动设备
- **📋 仪表板**: 多货币价格监控和趋势分析
- **🔍 详细分析**: 单个货币的深度分析和预测
- **📊 市值占比**: Top 10 加密货币市值分析
- **🎯 预测准确性**: 模型预测准确性分析

### 🛠️ 技术特性

- **🐳 Docker 化部署**: 一键部署到任何环境
- **⚡ 高性能**: Redis 缓存和异步任务处理
- **🔒 安全可靠**: HTTPS、CSRF 保护、SQL 注入防护
- **📈 可扩展**: 微服务架构，易于扩展新功能

## 🏗️ 技术架构

### 后端技术栈

- **框架**: Django 4.2 + Django REST Framework
- **数据库**: PostgreSQL (TimescaleDB)
- **缓存**: Redis
- **异步任务**: Celery + Redis
- **机器学习**: Facebook Prophet, Pandas, NumPy
- **API**: CoinGecko API

### 前端技术栈

- **框架**: Vue.js 3 + Composition API
- **构建工具**: Vite
- **图表库**: ECharts
- **UI 组件**: 自定义组件库
- **状态管理**: Pinia

### 部署技术栈

- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **SSL 证书**: Let's Encrypt (Certbot)
- **进程管理**: Gunicorn

## 🚀 快速开始

### 开发环境部署

#### 1. 克隆项目

\`\`\`bash
git clone https://github.com/yourusername/crypto-insight-dashboard.git
cd crypto-insight-dashboard
\`\`\`

#### 2. 配置环境变量

\`\`\`bash

# 复制环境变量模板

cp .env.example .env

# 编辑环境变量（可使用默认值进行开发）

nano .env
\`\`\`

#### 3. 启动服务

\`\`\`bash

# 启动所有服务

docker-compose up -d

# 查看服务状态

docker-compose ps
\`\`\`

#### 4. 初始化数据

\`\`\`bash

# 运行数据库迁移

docker-compose exec backend python manage.py migrate

# 创建超级用户

docker-compose exec backend python manage.py createsuperuser

# 添加默认货币

docker-compose exec backend python manage.py init_currencies
\`\`\`

#### 5. 访问应用

- **前端应用**: http://localhost:8080
- **后端 API**: http://localhost:8000/api
- **管理后台**: http://localhost:8000/admin

### 生产环境部署

详细的生产环境部署指南请参考: [deployment/README.md](deployment/README.md)

## 📚 使用指南

### Django Admin 管理界面

访问 `http://localhost:8000/admin` 使用 Django Admin 界面：

1. **添加货币**: 点击"添加默认货币"或手动添加新货币
2. **获取数据**: 点击货币旁的"📊 获取数据"按钮
3. **训练模型**: 点击货币旁的"🚀 训练模型"按钮
4. **完整流程**: 点击货币旁的"⚡ 完整流程"按钮（推荐）

详细操作指南请参考: [backend/ADMIN_GUIDE.md](backend/ADMIN_GUIDE.md)

### 管理命令

\`\`\`bash

# 初始化默认货币

docker-compose exec backend python manage.py init_currencies

# 运行完整数据获取和训练流程

docker-compose exec backend python manage.py run_pipeline

# 获取特定货币数据

docker-compose exec backend python manage.py fetch_data bitcoin

# 训练特定货币模型

docker-compose exec backend python manage.py train_model bitcoin
\`\`\`

## 📊 API 文档

### 主要 API 端点

\`\`\`
GET /api/currencies/ # 获取支持的货币列表
GET /api/market_data/ # 获取市场数据
GET /api/forecasts/ # 获取预测数据
GET /api/metrics/{id}/ # 获取货币指标
GET /api/market_share/ # 获取市值占比数据
\`\`\`

### 请求示例

\`\`\`bash

# 获取比特币市场数据

curl "http://localhost:8000/api/market_data/?currency_id=bitcoin"

# 获取比特币预测数据

curl "http://localhost:8000/api/forecasts/?currency_id=bitcoin"

# 获取比特币指标

curl "http://localhost:8000/api/metrics/bitcoin/"
\`\`\`

## 🔧 配置说明

### 环境变量

主要环境变量说明：

| 变量名                   | 说明            | 默认值                  |
| ------------------------ | --------------- | ----------------------- |
| \`DJANGO_DEBUG\`         | Django 调试模式 | \`True\`                |
| \`DJANGO_SECRET_KEY\`    | Django 密钥     | 随机生成                |
| \`DB_PASSWORD\`          | 数据库密码      | \`postgres\`            |
| \`DJANGO_ALLOWED_HOSTS\` | 允许的主机      | \`localhost,127.0.0.1\` |

### 定时任务

系统默认配置了以下定时任务：

- **每天 02:00**: 获取所有货币的最新数据
- **每天 03:00**: 重新训练所有模型
- **每小时**: 清理过期缓存

## 🛠️ 开发指南

### 项目结构

\`\`\`
crypto-insight-dashboard/
├── backend/ # Django 后端
│ ├── apps/ # Django 应用
│ │ ├── api/ # REST API
│ │ ├── market_data/ # 市场数据模型
│ │ ├── ml_predictions/# 机器学习预测
│ │ └── data_ingestion/# 数据获取
│ ├── config/ # Django 配置
│ └── models/ # 训练好的模型文件
├── frontend/ # Vue.js 前端
│ ├── src/
│ │ ├── components/ # Vue 组件
│ │ ├── views/ # 页面视图
│ │ ├── services/ # API 服务
│ │ └── stores/ # 状态管理
│ └── public/ # 静态资源
├── deployment/ # 部署配置
│ ├── nginx.conf # Nginx 配置
│ ├── deploy.sh # 部署脚本
│ └── README.md # 部署文档
└── docker-compose.yml # Docker 编排文件
\`\`\`

### 添加新货币

1. **通过 Admin 界面**: 最简单的方法
2. **通过 API**: POST 到 \`/admin/market_data/currency/add/\`
3. **通过管理命令**: 修改 \`init_currencies.py\`

### 自定义模型

在 \`apps/ml_predictions/models.py\` 中可以：

- 修改 Prophet 模型参数
- 添加新的特征变量
- 实现其他机器学习算法

## 🧪 测试

\`\`\`bash

# 运行后端测试

docker-compose exec backend python manage.py test

# 运行前端测试

cd frontend && npm run test

# 代码质量检查

docker-compose exec backend flake8
cd frontend && npm run lint
\`\`\`

## 📈 监控和日志

### 查看日志

\`\`\`bash

# 查看所有服务日志

docker-compose logs -f

# 查看特定服务日志

docker-compose logs -f backend
docker-compose logs -f celery_worker
\`\`\`

### 性能监控

- **系统资源**: \`docker stats\`
- **数据库性能**: PostgreSQL 慢查询日志
- **缓存命中率**: Redis INFO 命令
- **任务队列**: Celery Flower (可选安装)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (\`git checkout -b feature/AmazingFeature\`)
3. 提交更改 (\`git commit -m 'Add some AmazingFeature'\`)
4. 推送到分支 (\`git push origin feature/AmazingFeature\`)
5. 开启 Pull Request

## 📜 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

如果您遇到问题或有建议：

1. 查看 [Issues](https://github.com/yourusername/crypto-insight-dashboard/issues)
2. 创建新的 Issue
3. 联系维护者

## 🙏 致谢

- [CoinGecko](https://www.coingecko.com/) - 提供免费的加密货币 API
- [Facebook Prophet](https://facebook.github.io/prophet/) - 优秀的时间序列预测库
- [Django](https://www.djangoproject.com/) - 强大的 Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [ECharts](https://echarts.apache.org/) - 强大的图表库

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/yourusername/crypto-insight-dashboard)
![GitHub forks](https://img.shields.io/github/forks/yourusername/crypto-insight-dashboard)
![GitHub issues](https://img.shields.io/github/issues/yourusername/crypto-insight-dashboard)
![GitHub license](https://img.shields.io/github/license/yourusername/crypto-insight-dashboard)

---

⭐ 如果这个项目对您有帮助，请给它一个星标！
