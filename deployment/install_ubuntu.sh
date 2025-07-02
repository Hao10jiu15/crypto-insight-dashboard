#!/bin/bash
# Ubuntu 22.04 快速环境安装脚本 - 针对Docker 26.1.3优化

set -e

# 彩色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo -e "${BLUE}🚀 Ubuntu 22.04 快速环境安装${NC}"

# 显示系统信息
log_info "系统信息："
uname -a
lsb_release -a

# 更新系统
log_info "更新系统包..."
sudo apt update && sudo apt upgrade -y
log_success "系统更新完成"

# 安装必要工具
log_info "安装基础工具..."
sudo apt install -y curl wget gnupg lsb-release ca-certificates apt-transport-https software-properties-common
log_success "基础工具安装完成"

# 安装Docker CE (最新稳定版)
log_info "安装Docker CE..."

# 卸载旧版本
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加Docker仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新包索引
sudo apt update

# 安装Docker CE
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER

# 验证Docker安装
DOCKER_VERSION=$(docker --version)
log_success "Docker安装完成: $DOCKER_VERSION"

# 安装Docker Compose (独立版本)
log_info "安装Docker Compose..."
COMPOSE_VERSION="v2.24.0"
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证Docker Compose
COMPOSE_VER=$(docker-compose --version)
log_success "Docker Compose安装完成: $COMPOSE_VER"

# 安装Nginx
log_info "安装Nginx..."
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
NGINX_VERSION=$(nginx -v 2>&1)
log_success "Nginx安装完成: $NGINX_VERSION"

# 安装Certbot
log_info "安装Certbot..."
sudo apt install -y certbot python3-certbot-nginx
CERTBOT_VERSION=$(certbot --version)
log_success "Certbot安装完成: $CERTBOT_VERSION"

# 安装Git
log_info "安装Git..."
sudo apt install -y git
GIT_VERSION=$(git --version)
log_success "Git安装完成: $GIT_VERSION"

# 配置防火墙
log_info "配置UFW防火墙..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
log_success "防火墙配置完成"

# 验证安装
echo ""
log_info "验证安装..."
echo ""

# 显示版本信息
echo -e "${BLUE}📋 安装组件版本：${NC}"
echo "  Docker: $(docker --version)"
echo "  Docker Compose: $(docker-compose --version)"
echo "  Nginx: $(nginx -v 2>&1)"
echo "  Certbot: $(certbot --version)"
echo "  Git: $(git --version)"

# 检查服务状态
echo ""
echo -e "${BLUE}📊 服务状态：${NC}"
for service in docker nginx; do
    if systemctl is-active --quiet $service; then
        log_success "$service: 运行中"
    else
        log_error "$service: 未运行"
    fi
done

# 显示UFW状态
echo ""
echo -e "${BLUE}🔥 防火墙状态：${NC}"
sudo ufw status numbered

echo ""
log_success "🎉 Ubuntu 22.04 环境安装完成！"
echo ""
log_warning "重要提示："
log_warning "1. 请执行 'exit' 退出当前SSH会话"
log_warning "2. 重新登录SSH以使Docker权限生效"
log_warning "3. 重新登录后运行部署脚本："
echo -e "${BLUE}   curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash${NC}"
