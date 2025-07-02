#!/bin/bash
# 紧急修复Docker镜像下载问题

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

echo -e "${BLUE}🌐 修复Docker镜像下载问题...${NC}"

# 1. 停止所有Docker服务
log_info "停止Docker服务..."
sudo systemctl stop docker

# 2. 配置Docker镜像加速器
log_info "配置Docker镜像加速器..."
sudo mkdir -p /etc/docker

# 备份原有配置
if [ -f /etc/docker/daemon.json ]; then
    sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak
fi

# 写入新的镜像加速配置
cat << 'EOF' | sudo tee /etc/docker/daemon.json
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com", 
        "https://reg-mirror.qiniu.com",
        "https://registry.docker-cn.com",
        "https://mirror.baidubce.com",
        "https://dockerproxy.com"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF

# 3. 重启Docker服务
log_info "重启Docker服务..."
sudo systemctl daemon-reload
sudo systemctl start docker
sudo systemctl enable docker

# 等待Docker服务启动
sleep 10

# 4. 验证Docker服务
if ! systemctl is-active --quiet docker; then
    log_error "Docker服务启动失败"
    exit 1
fi
log_success "Docker服务已重启"

# 5. 测试镜像拉取
log_info "测试镜像加速器..."
if timeout 30 docker pull hello-world > /dev/null 2>&1; then
    log_success "镜像加速器工作正常"
    docker rmi hello-world > /dev/null 2>&1 || true
else
    log_warning "镜像拉取测试失败，但继续尝试部署"
fi

# 6. 进入项目目录
cd /opt/crypto-prediction

# 7. 预拉取所需镜像（使用国内镜像源）
log_info "预拉取基础镜像..."

# 基础镜像列表
IMAGES=(
    "python:3.11-slim"
    "python:3.11"
    "node:18-alpine"
    "nginx:alpine"
    "postgres:15"
    "redis:7-alpine"
)

for image in "${IMAGES[@]}"; do
    log_info "拉取镜像: $image"
    if timeout 60 docker pull "$image"; then
        log_success "✅ $image"
    else
        log_warning "⚠️  $image 拉取失败，稍后重试"
    fi
done

# 8. 尝试重新构建
log_info "重新构建服务..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 设置构建超时
export DOCKER_CLIENT_TIMEOUT=300
export COMPOSE_HTTP_TIMEOUT=300

# 清理构建缓存
docker builder prune -f

# 逐个服务构建（避免并发导致网络问题）
SERVICES=("backend" "frontend" "celery" "celery_beat")

for service in "${SERVICES[@]}"; do
    log_info "构建服务: $service"
    if timeout 600 docker compose -f docker-compose.prod.yml build --no-cache "$service"; then
        log_success "✅ $service 构建成功"
    else
        log_error "❌ $service 构建失败"
        # 显示详细错误信息
        docker compose -f docker-compose.prod.yml logs "$service" 2>/dev/null || true
    fi
done

# 9. 启动所有服务
log_info "启动所有服务..."
docker compose -f docker-compose.prod.yml up -d

# 10. 等待服务启动
log_info "等待服务启动..."
sleep 30

# 11. 检查服务状态
log_info "检查服务状态..."
docker compose -f docker-compose.prod.yml ps

# 12. 运行初始化任务
log_info "运行数据库迁移..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

log_info "创建管理员用户..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("✅ 管理员用户已创建: admin / admin123456")
else:
    print("ℹ️  管理员用户已存在")
EOF

log_info "收集静态文件..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

log_info "初始化货币数据..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py init_currencies

# 13. 健康检查
log_info "健康检查..."
sleep 10

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

if curl -f http://localhost/api/currencies/ > /dev/null 2>&1; then
    log_success "后端API正常运行"
else
    log_error "后端API访问失败"
    echo "查看后端日志:"
    docker compose -f docker-compose.prod.yml logs backend --tail=20
fi

if curl -f http://localhost/ > /dev/null 2>&1; then
    log_success "前端应用正常运行"
else
    log_error "前端应用访问失败"
    echo "查看前端日志:"
    docker compose -f docker-compose.prod.yml logs nginx --tail=20
fi

echo ""
echo "🎉 修复完成！"
echo ""
echo "📋 部署信息："
echo "   🌐 网站地址: http://$SERVER_IP"
echo "   🔧 管理后台: http://$SERVER_IP/admin"
echo "   👤 管理员账号: admin / admin123456"
echo ""
echo "📊 状态检查命令："
echo "   docker compose -f /opt/crypto-prediction/docker-compose.prod.yml ps"
echo "   docker compose -f /opt/crypto-prediction/docker-compose.prod.yml logs"
echo ""
echo "🔧 如果仍有问题："
echo "   1. 检查防火墙设置: sudo ufw status"
echo "   2. 查看详细日志: docker compose logs [service_name]"
echo "   3. 重启服务: docker compose restart [service_name]"
echo ""
