#!/bin/bash
# GitHub部署脚本 - 从GitHub克隆并部署 (优化版本)

set -e  # 遇到错误立即退出

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

echo -e "${BLUE}🚀 开始从GitHub部署加密货币预测系统...${NC}"

# 配置变量
REPO_URL="https://github.com/Hao10jiu15/crypto-insight-dashboard.git"
DEPLOY_DIR="/opt/crypto-prediction"
BRANCH="master"

# 显示部署信息
log_info "部署配置："
echo "  仓库地址: $REPO_URL"
echo "  部署目录: $DEPLOY_DIR" 
echo "  分支: $BRANCH"
echo "  当前用户: $(whoami)"
echo "  系统信息: $(uname -a | cut -d' ' -f1-3)"

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    log_warning "不建议使用root用户运行此脚本"
    log_warning "建议使用普通用户并确保该用户在docker组中"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "部署已取消"
        exit 1
    fi
fi

# 检查必要的命令
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先运行环境安装脚本"
        log_info "运行: curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_server.sh | bash"
        exit 1
    fi
    log_success "$1 已安装: $(command -v $1)"
}

log_info "检查必要的工具..."
check_command git
check_command docker
check_command docker-compose

# 检查Docker服务状态
if ! systemctl is-active --quiet docker; then
    log_error "Docker服务未运行，请启动Docker服务"
    log_info "运行: sudo systemctl start docker"
    exit 1
fi
log_success "Docker服务正在运行"

# 检查用户是否在docker组中
if ! groups | grep -q docker; then
    log_error "当前用户不在docker组中"
    log_info "请运行: sudo usermod -aG docker $(whoami)"
    log_info "然后重新登录SSH"
    exit 1
fi
log_success "用户已在docker组中"

# 停止现有服务（如果存在）
echo "🛑 停止现有服务..."
if [ -d "$DEPLOY_DIR" ]; then
    cd "$DEPLOY_DIR"
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
fi

# 创建部署目录
echo "📁 创建部署目录..."
sudo mkdir -p "$DEPLOY_DIR"
sudo chown $USER:$USER "$DEPLOY_DIR"

# 克隆或更新代码
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "🔄 更新现有代码..."
    cd "$DEPLOY_DIR"
    git fetch origin
    git reset --hard origin/$BRANCH
    git clean -fd
else
    echo "📥 克隆代码仓库..."
    git clone -b $BRANCH "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

echo "✅ 代码更新完成"

# 检查配置文件
echo "🔧 检查配置文件..."
if [ ! -f ".env.production" ]; then
    echo "📝 创建生产环境配置文件..."
    cp .env.production.example .env.production
    
    echo "⚠️  重要：请编辑 .env.production 文件并配置以下项目："
    echo "   - DB_PASSWORD (数据库密码)"
    echo "   - DJANGO_SECRET_KEY (Django密钥)"
    echo "   - DJANGO_ALLOWED_HOSTS (您的域名)"
    echo "   - EMAIL_* (邮件配置，可选)"
    echo ""
    echo "配置文件位置: $DEPLOY_DIR/.env.production"
    echo ""
    read -p "配置完成后按回车继续..." -r
fi

# 检查域名配置
echo "🌐 检查域名配置..."
if grep -q "yourdomain.com" deployment/nginx.conf; then
    echo "⚠️  请更新 deployment/nginx.conf 中的域名配置"
    echo "将 'yourdomain.com' 替换为您的实际域名"
    read -p "更新完成后按回车继续..." -r
fi

if grep -q "yourdomain.com" frontend/Dockerfile.prod; then
    echo "⚠️  请更新 frontend/Dockerfile.prod 中的API地址"
    echo "将 'yourdomain.com' 替换为您的实际域名"
    read -p "更新完成后按回车继续..." -r
fi

# 生成Django密钥（如果需要）
if grep -q "CHANGE_THIS_VERY_SECURE_SECRET_KEY" .env.production; then
    echo "🔐 生成Django密钥..."
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sed -i "s/CHANGE_THIS_VERY_SECURE_SECRET_KEY/$SECRET_KEY/g" .env.production
    echo "✅ Django密钥已生成"
fi

# 清理旧的镜像和容器
echo "🧹 清理旧的容器和镜像..."
docker-compose -f docker-compose.prod.yml down --volumes --remove-orphans 2>/dev/null || true
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
import os
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("✅ 管理员用户已创建: admin / admin123456")
else:
    print("ℹ️  管理员用户已存在")
EOF

# 收集静态文件
echo "📦 收集静态文件..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# 初始化默认货币
echo "💰 初始化默认货币..."
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py init_currencies

# 给脚本执行权限
chmod +x deployment/manage.sh

# 检查应用健康状态
echo "🏥 检查应用健康状态..."
sleep 10

if curl -f http://localhost/api/currencies/ > /dev/null 2>&1; then
    echo "✅ 后端API正常运行"
else
    echo "❌ 后端API访问失败"
    echo "检查日志: docker-compose -f docker-compose.prod.yml logs backend"
fi

if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ 前端应用正常运行"
else
    echo "❌ 前端应用访问失败"
    echo "检查日志: docker-compose -f docker-compose.prod.yml logs nginx"
fi

# 显示部署信息
echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 部署信息："
echo "   📂 部署目录: $DEPLOY_DIR"
echo "   🌐 网站地址: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')"
echo "   🔧 管理后台: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')/admin"
echo "   👤 管理员账号: admin / admin123456"
echo ""
echo "🔒 SSL证书配置："
echo "   运行以下命令申请SSL证书："
echo "   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo "   或者使用: ./deployment/manage.sh ssl"
echo ""
echo "📊 监控命令："
echo "   查看日志: ./deployment/manage.sh logs"
echo "   查看状态: ./deployment/manage.sh status"
echo "   重启服务: ./deployment/manage.sh restart"
echo "   备份数据: ./deployment/manage.sh backup"
echo "   更新应用: ./deployment/manage.sh update"
echo ""
echo "⚠️  请记得："
echo "   1. 修改默认管理员密码"
echo "   2. 配置SSL证书"
echo "   3. 设置防火墙规则"
echo "   4. 定期备份数据库"
echo "   5. 监控系统资源使用"
echo ""
echo "🎯 下一步："
echo "   1. 访问网站确认部署成功"
echo "   2. 登录管理后台添加货币"
echo "   3. 运行完整流程获取数据和训练模型"
echo ""
echo "📚 更多信息请参考: $DEPLOY_DIR/deployment/README.md"
