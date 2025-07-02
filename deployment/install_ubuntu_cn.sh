#!/bin/bash
# Ubuntu 22.04 中国网络环境优化安装脚本 - 非交互模式

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

echo -e "${BLUE}🚀 Ubuntu 22.04 中国网络环境优化安装（非交互模式）${NC}"

# 显示系统信息
log_info "系统信息："
uname -a
lsb_release -a

# 备份并配置APT镜像源（阿里云）
log_info "配置APT镜像源（阿里云）..."
sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup 2>/dev/null || true

cat << 'EOF' | sudo tee /etc/apt/sources.list
# 阿里云Ubuntu镜像源
deb https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse

deb https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse

deb https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse

deb https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
EOF

log_success "APT镜像源配置完成"

# 更新系统
log_info "更新系统包（非交互模式）..."
sudo apt update
sudo apt upgrade -yq --force-yes
log_success "系统更新完成"

# 安装基础工具
log_info "安装基础工具（非交互模式）..."
sudo apt install -yq --no-install-recommends curl wget gnupg lsb-release ca-certificates apt-transport-https software-properties-common python3-pip
log_success "基础工具安装完成"

# 配置pip镜像源
log_info "配置pip镜像源..."
mkdir -p ~/.pip
cat << 'EOF' > ~/.pip/pip.conf
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
log_success "pip镜像源配置完成"

# 安装Docker（使用阿里云镜像）
log_info "安装Docker CE（阿里云镜像）..."

# 卸载旧版本
sudo apt remove -yq docker docker-engine docker.io containerd runc 2>/dev/null || true

# 添加Docker官方GPG密钥（使用阿里云镜像）
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库（阿里云镜像）
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新包索引
sudo apt update

# 安装Docker CE（非交互模式）
sudo apt install -yq --no-install-recommends docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER

# 验证Docker安装
DOCKER_VERSION=$(docker --version)
log_success "Docker安装完成: $DOCKER_VERSION"

# 配置Docker镜像加速
log_info "配置Docker镜像加速..."
sudo mkdir -p /etc/docker
cat << 'EOF' | sudo tee /etc/docker/daemon.json
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://reg-mirror.qiniu.com",
        "https://registry.docker-cn.com",
        "https://mirror.baidubce.com"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "storage-driver": "overlay2"
}
EOF

# 重启Docker服务应用镜像配置
sudo systemctl daemon-reload
sudo systemctl restart docker
log_success "Docker镜像加速配置完成"

# 安装Docker Compose（使用pip，更稳定）
log_info "安装Docker Compose（使用pip）..."
sudo pip3 install docker-compose
if [ $? -eq 0 ]; then
    COMPOSE_VER=$(docker-compose --version)
    log_success "Docker Compose安装完成: $COMPOSE_VER"
else
    log_error "Docker Compose安装失败！"
    exit 1
fi

# 安装Nginx
log_info "安装Nginx（非交互模式）..."
sudo apt install -yq --no-install-recommends nginx
sudo systemctl start nginx
sudo systemctl enable nginx
NGINX_VERSION=$(nginx -v 2>&1)
log_success "Nginx安装完成: $NGINX_VERSION"

# 安装Certbot
log_info "安装Certbot（非交互模式）..."
sudo apt install -yq --no-install-recommends certbot python3-certbot-nginx
CERTBOT_VERSION=$(certbot --version)
log_success "Certbot安装完成: $CERTBOT_VERSION"

# 安装Git
log_info "安装Git（非交互模式）..."
sudo apt install -yq --no-install-recommends git
GIT_VERSION=$(git --version)
log_success "Git安装完成: $GIT_VERSION"

# 配置防火墙（非交互模式）
log_info "配置UFW防火墙（非交互模式）..."
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

# 显示Docker镜像加速状态
echo ""
echo -e "${BLUE}🐳 Docker镜像加速状态：${NC}"
docker info | grep -A 5 "Registry Mirrors" || echo "  镜像加速已配置"

echo ""
log_success "🎉 Ubuntu 22.04 中国网络环境优化安装完成！"
echo ""
log_warning "重要提示："
log_warning "1. 请执行 'exit' 退出当前SSH会话"
log_warning "2. 重新登录SSH以使Docker权限生效"
log_warning "3. 重新登录后运行部署脚本："
echo -e "${BLUE}   curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash${NC}"
echo ""
log_info "💡 提示：此脚本已优化中国网络环境，包括："
echo "  - 阿里云APT镜像源"
echo "  - 清华大学pip镜像源"
echo "  - 阿里云Docker仓库"
echo "  - 多个Docker镜像加速器"
echo "  - 全程非交互模式安装"

# 恢复交互模式（可选）
# unset DEBIAN_FRONTEND
