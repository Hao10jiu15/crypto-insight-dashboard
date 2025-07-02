#!/bin/bash
# Ubuntu 22.04 快速安装脚本 - 完全非交互模式（已优化网络和稳定性）

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
# 使用 dist-upgrade 更全面地处理依赖关系，解决类似 cloud-init 被搁置的问题
sudo apt dist-upgrade -yq 2>/dev/null

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

# 安装Docker
log_info "安装Docker..."
# 先移除可能冲突的旧版或系统自带包
sudo apt remove -yq docker docker-engine docker.io containerd runc 2>/dev/null || true
sudo apt autoremove -yq 2>/dev/null || true

# 添加Docker GPG密钥（使用阿里云镜像以提高稳定性）
sudo mkdir -p /etc/apt/keyrings
# 强制删除旧文件以避免交互式提示
sudo rm -f /etc/apt/keyrings/docker.gpg
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加Docker仓库（使用阿里云镜像）
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新包索引
sudo apt update -qq

# 安装Docker Engine
log_info "安装最新版Docker Engine..."
sudo apt install -yq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动并设置Docker开机自启
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

log_info "Docker Compose已作为插件随Docker安装..."

# 安装Nginx
log_info "安装Nginx..."
sudo apt install -yq --no-install-recommends nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 配置防火墙
log_info "配置防火墙..."
sudo apt install -yq --no-install-recommends ufw
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 验证安装
echo ""
log_info "验证安装..."
echo ""

if command -v docker &> /dev/null; then
    log_success "Docker: $(docker --version)"
else
    log_error "Docker安装失败"
fi

if docker compose version &> /dev/null; then
    log_success "Docker Compose: $(docker compose version)"
elif command -v docker-compose &> /dev/null; then
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