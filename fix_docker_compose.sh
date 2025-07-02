#!/bin/bash
# 快速修复Docker Compose兼容性问题并重新部署

set -e

# 彩色输出函数
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo -e "${BLUE}🔧 修复Docker Compose兼容性问题...${NC}"

# 1. 卸载旧版本的docker-compose
log_info "卸载旧版本的docker-compose..."
sudo pip3 uninstall docker-compose -y 2>/dev/null || true
sudo rm -f /usr/local/bin/docker-compose

# 2. 确保使用Docker Compose Plugin
log_info "验证Docker Compose Plugin..."
if docker compose version &> /dev/null; then
    log_success "Docker Compose Plugin可用: $(docker compose version)"
else
    log_error "Docker Compose Plugin不可用，需要重新安装Docker"
    log_info "运行以下命令重新安装："
    echo "sudo apt remove -y docker.io containerd runc"
    echo "curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_quick.sh | bash"
    exit 1
fi

# 3. 进入项目目录
cd /opt/crypto-prediction

# 4. 清理现有服务
log_info "清理现有服务..."
docker compose -f docker-compose.prod.yml down --volumes --remove-orphans 2>/dev/null || true
docker system prune -af

# 5. 重新构建和启动服务
log_info "构建并启动服务..."
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# 6. 等待服务启动
log_info "等待服务启动..."
sleep 30

# 7. 检查服务状态
log_info "检查服务状态..."
docker compose -f docker-compose.prod.yml ps

# 8. 运行数据库迁移
log_info "运行数据库迁移..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# 9. 创建管理员用户
log_info "创建管理员用户..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("✅ 管理员用户已创建: admin / admin123456")
else:
    print("ℹ️  管理员用户已存在")
EOF

# 10. 收集静态文件
log_info "收集静态文件..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# 11. 初始化货币数据
log_info "初始化货币数据..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py init_currencies

# 12. 健康检查
log_info "健康检查..."
sleep 10

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

if curl -f http://localhost/api/currencies/ > /dev/null 2>&1; then
    log_success "后端API正常运行"
else
    log_error "后端API访问失败"
    docker compose -f docker-compose.prod.yml logs backend
fi

if curl -f http://localhost/ > /dev/null 2>&1; then
    log_success "前端应用正常运行"
else
    log_error "前端应用访问失败"
    docker compose -f docker-compose.prod.yml logs nginx
fi

echo ""
echo "🎉 修复完成！"
echo ""
echo "📋 部署信息："
echo "   🌐 网站地址: http://$SERVER_IP"
echo "   🔧 管理后台: http://$SERVER_IP/admin"
echo "   👤 管理员账号: admin / admin123456"
echo ""
echo "📊 常用命令："
echo "   查看状态: cd /opt/crypto-prediction && docker compose -f docker-compose.prod.yml ps"
echo "   查看日志: cd /opt/crypto-prediction && docker compose -f docker-compose.prod.yml logs"
echo "   重启服务: cd /opt/crypto-prediction && docker compose -f docker-compose.prod.yml restart"
echo ""
