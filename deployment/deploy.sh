#!/bin/bash
# 生产环境部署脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署加密货币预测系统到生产环境..."

# 检查必要的环境变量
if [ ! -f .env.production ]; then
    echo "❌ 错误：找不到 .env.production 文件"
    echo "请先创建并配置 .env.production 文件"
    exit 1
fi

# 创建必要的目录
echo "📁 创建目录结构..."
sudo mkdir -p /var/www/crypto-prediction
sudo mkdir -p /var/log/crypto-prediction
sudo mkdir -p ./deployment/ssl

# 设置权限
sudo chown -R $USER:$USER /var/www/crypto-prediction

# 停止现有服务（如果存在）
echo "🛑 停止现有服务..."
docker-compose -f docker-compose.prod.yml down || true

# 清理旧的镜像（可选）
echo "🧹 清理旧镜像..."
docker system prune -f

# 构建和启动服务
echo "🔨 构建并启动服务..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 运行数据库迁移
echo "🗃️ 运行数据库迁移..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# 创建超级用户（如果不存在）
echo "👤 创建管理员用户..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("管理员用户已创建: admin / admin123456")
else:
    print("管理员用户已存在")
EOF

# 收集静态文件
echo "📦 收集静态文件..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# 检查应用健康状态
echo "🏥 检查应用健康状态..."
sleep 10

if curl -f http://localhost/api/currencies/ > /dev/null 2>&1; then
    echo "✅ 后端API正常运行"
else
    echo "❌ 后端API访问失败"
fi

if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ 前端应用正常运行"
else
    echo "❌ 前端应用访问失败"
fi

echo "🎉 部署完成！"
echo ""
echo "📋 部署信息："
echo "   🌐 网站地址: http://your-server-ip"
echo "   🔧 管理后台: http://your-server-ip/admin"
echo "   👤 管理员账号: admin / admin123456"
echo ""
echo "🔒 SSL证书配置："
echo "   运行以下命令申请SSL证书："
echo "   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo ""
echo "📊 监控命令："
echo "   查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "   查看状态: docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "⚠️  请记得："
echo "   1. 修改默认管理员密码"
echo "   2. 配置SSL证书"
echo "   3. 设置防火墙规则"
echo "   4. 定期备份数据库"
