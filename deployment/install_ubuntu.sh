#!/bin/bash
# Ubuntu 22.04 快速环境安装脚本 - 针对Docker 26.1.3优化（非交互模式）

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

echo -e "${BLUE}🚀 Ubuntu 22.04 快速环境安装（非交互模式）${NC}"

# 显示系统信息
log_info "系统信息："
uname -a
lsb_release -a

# 更新系统
log_info "更新系统包（非交互模式）..."
sudo apt update
sudo apt upgrade -yq
log_success "系统更新完成"

# 安装必要工具
log_info "安装基础工具（非交互模式）..."
sudo apt install -yq curl wget gnupg lsb-release ca-certificates apt-transport-https software-properties-common python3-pip
log_success "基础工具安装完成"

# 安装Docker CE (最新稳定版)
log_info "安装Docker CE..."

# 卸载旧版本和可能冲突的包
sudo apt remove -yq docker docker-engine docker.io containerd runc 2>/dev/null || true
sudo apt autoremove -yq 2>/dev/null || true

# 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加Docker仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新包索引
sudo apt update

# 安装Docker CE（非交互模式）
sudo apt install -yq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

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
        "https://registry.docker-cn.com"
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

# Docker Compose现在已包含在docker-compose-plugin中
log_info "验证Docker Compose..."
if docker compose version &> /dev/null; then
    COMPOSE_VER=$(docker compose version)
    log_success "Docker Compose安装完成: $COMPOSE_VER"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VER=$(docker-compose --version)
    log_success "Docker Compose（独立版本）: $COMPOSE_VER"
else
    log_warning "Docker Compose未找到，尝试下载独立版本..."
    COMPOSE_VERSION="v2.24.0"
    
    # 定义多个下载源（按优先级排序）
    DOWNLOAD_URLS=(
        "https://ghproxy.com/https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64"
        "https://mirror.ghproxy.com/https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64"
        "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64"
        "https://get.daocloud.io/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64"
    )
    
    # 尝试从不同源下载
    DOWNLOAD_SUCCESS=false
    for url in "${DOWNLOAD_URLS[@]}"; do
        log_info "尝试从镜像源下载: $(echo $url | cut -d'/' -f3)"
        if sudo curl -L --connect-timeout 10 --max-time 60 "$url" -o /usr/local/bin/docker-compose 2>/dev/null; then
            if [ -s /usr/local/bin/docker-compose ]; then
                DOWNLOAD_SUCCESS=true
                sudo chmod +x /usr/local/bin/docker-compose
                log_success "Docker Compose下载成功！"
                break
            else
                log_warning "下载的文件为空，尝试下一个源..."
                sudo rm -f /usr/local/bin/docker-compose
            fi
        else
            log_warning "下载失败，尝试下一个源..."
        fi
    done
    
    if [ "$DOWNLOAD_SUCCESS" = false ]; then
        log_warning "所有下载源都失败，使用pip安装..."
        sudo pip3 install docker-compose -i https://pypi.tuna.tsinghua.edu.cn/simple/
        if [ $? -ne 0 ]; then
            log_error "Docker Compose安装失败！"
            exit 1
        fi
    fi
    
    # 最终验证
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VER=$(docker-compose --version)
        log_success "Docker Compose安装完成: $COMPOSE_VER"
    else
        log_error "Docker Compose安装验证失败！"
        exit 1
    fi
fi

# 安装Nginx
log_info "安装Nginx（非交互模式）..."
sudo apt install -yq nginx
sudo systemctl start nginx
sudo systemctl enable nginx
NGINX_VERSION=$(nginx -v 2>&1)
log_success "Nginx安装完成: $NGINX_VERSION"

# 安装Certbot
log_info "安装Certbot（非交互模式）..."
sudo apt install -yq certbot python3-certbot-nginx
CERTBOT_VERSION=$(certbot --version)
log_success "Certbot安装完成: $CERTBOT_VERSION"

# 安装Git
log_info "安装Git（非交互模式）..."
sudo apt install -yq git
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

echo ""
log_success "🎉 Ubuntu 22.04 环境安装完成！"
echo ""
log_warning "重要提示："
log_warning "1. 请执行 'exit' 退出当前SSH会话"
log_warning "2. 重新登录SSH以使Docker权限生效"
log_warning "3. 重新登录后运行部署脚本："
echo -e "${BLUE}   curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash${NC}"
