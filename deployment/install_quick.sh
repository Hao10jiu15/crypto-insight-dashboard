#!/bin/bash
# Ubuntu 22.04 快速安装脚本 - 完全非交互模式

set -e

# 设置非交互模式
export DEBIAN_FRONTEND=noninteractive

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

echo -e "${BLUE}🚀 Ubuntu 22.04 快速安装（完全非交互模式）${NC}"

# 清理可能的锁定
sudo killall -9 apt apt-get dpkg 2>/dev/null || true
sudo dpkg --configure -a 2>/dev/null || true
sudo apt --fix-broken install -y 2>/dev/null || true

# 更新系统
log_info "更新系统..."
sudo apt update -qq
sudo apt upgrade -yq 2>/dev/null

# 安装基础工具
log_info "安装基础工具..."
sudo apt install -yq --no-install-recommends \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    ca-certificates \
    gnupg \
    lsb-release

# 安装Docker（使用apt仓库中的版本，避免复杂配置）
log_info "安装Docker..."
sudo apt install -yq --no-install-recommends docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 安装Docker Compose（使用pip，最稳定）
log_info "安装Docker Compose..."
sudo pip3 install docker-compose -q

# 安装Nginx
log_info "安装Nginx..."
sudo apt install -yq --no-install-recommends nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 配置防火墙
log_info "配置防火墙..."
sudo apt install -yq --no-install-recommends ufw
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 验证安装
echo ""
log_info "验证安装..."
echo ""

if command -v docker &> /dev/null; then
    log_success "Docker: $(docker --version)"
else
    log_error "Docker安装失败"
fi

if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose: $(docker-compose --version)"
else
    log_error "Docker Compose安装失败"
fi

if command -v nginx &> /dev/null; then
    log_success "Nginx: $(nginx -v 2>&1)"
else
    log_error "Nginx安装失败"
fi

if command -v git &> /dev/null; then
    log_success "Git: $(git --version)"
else
    log_error "Git安装失败"
fi

echo ""
log_success "🎉 快速安装完成！"
echo ""
log_warning "重要提示："
log_warning "1. 请执行 'exit' 退出当前SSH会话"
log_warning "2. 重新登录SSH以使Docker权限生效"
log_warning "3. 重新登录后运行部署脚本："
echo -e "${BLUE}   curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash${NC}"

# 恢复交互模式
unset DEBIAN_FRONTEND
