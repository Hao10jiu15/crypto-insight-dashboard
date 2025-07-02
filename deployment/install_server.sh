#!/bin/bash
# 服务器环境安装脚本 - 针对Ubuntu 22.04优化

set -e  # 遇到错误立即退出

# 彩色输出函数
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}🚀 开始安装服务器环境...${NC}"
echo -e "${BLUE}📋 系统信息：${NC}"

# 显示系统信息
log_info "检测系统信息..."
uname -a
cat /etc/os-release | grep PRETTY_NAME

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
    else
        OS=$(uname -s)
    fi
    
    case "$OS" in
        *"Ubuntu"*|*"Debian"*)
            PACKAGE_MANAGER="apt"
            INSTALL_CMD="apt install -y"
            UPDATE_CMD="apt update && apt upgrade -y"
            log_success "检测到Ubuntu/Debian系统"
            ;;
        *"CentOS"*|*"Red Hat"*|*"Rocky"*|*"AlmaLinux"*)
            PACKAGE_MANAGER="dnf"
            INSTALL_CMD="dnf install -y"
            UPDATE_CMD="dnf update -y"
            log_success "检测到CentOS/RHEL系统"
            ;;
        *"Alibaba Cloud Linux"*|*"Alinux"*|*"alinux"*)
            PACKAGE_MANAGER="yum"
            INSTALL_CMD="yum install -y"
            UPDATE_CMD="yum update -y"
            log_success "检测到阿里云Linux系统"
            ;;
        *)
            log_warning "未知操作系统: $OS，尝试自动检测包管理器..."
            if command -v apt &> /dev/null; then
                log_info "检测到apt，使用Ubuntu/Debian模式"
                PACKAGE_MANAGER="apt"
                INSTALL_CMD="apt install -y"
                UPDATE_CMD="apt update && apt upgrade -y"
            elif command -v yum &> /dev/null; then
                log_info "检测到yum，使用RHEL兼容模式"
                PACKAGE_MANAGER="yum"
                INSTALL_CMD="yum install -y"
                UPDATE_CMD="yum update -y"
            elif command -v dnf &> /dev/null; then
                log_info "检测到dnf，使用Fedora模式"
                PACKAGE_MANAGER="dnf"
                INSTALL_CMD="dnf install -y"
                UPDATE_CMD="dnf update -y"
            else
                log_error "无法检测到支持的包管理器"
                exit 1
            fi
            ;;
    esac
    
    log_success "操作系统: $OS"
    log_success "包管理器: $PACKAGE_MANAGER"
}

detect_os

# 更新系统包
log_info "更新系统包..."
echo "执行命令: sudo $UPDATE_CMD"
sudo $UPDATE_CMD
log_success "系统包更新完成"

# 安装基础工具
log_info "安装基础工具..."
sudo $INSTALL_CMD curl wget gnupg lsb-release ca-certificates
log_success "基础工具安装完成"

# 检查Docker是否已存在
check_docker() {
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log_warning "Docker已安装: $DOCKER_VERSION"
        
        # 检查Docker服务状态
        if systemctl is-active --quiet docker; then
            log_success "Docker服务正在运行"
        else
            log_warning "Docker服务未运行，正在启动..."
            sudo systemctl start docker
            sudo systemctl enable docker
        fi
        return 0
    else
        return 1
    fi
}

# 安装Docker
log_info "检查Docker安装状态..."
if ! check_docker; then
    log_info "开始安装Docker..."
    
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        # Ubuntu系统优化安装
        log_info "Ubuntu系统，使用官方APT仓库安装Docker..."
        
        # 添加Docker的官方GPG密钥
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # 添加Docker仓库
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 更新包索引
        sudo apt update
        
        # 安装Docker CE
        sudo $INSTALL_CMD docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
    elif [ "$PACKAGE_MANAGER" = "yum" ]; then
        # 阿里云Linux特殊处理
        log_info "使用yum安装Docker..."
        sudo $INSTALL_CMD docker
        
        # 如果失败，尝试添加Docker CE仓库
        if [ $? -ne 0 ]; then
            log_info "尝试添加Docker CE仓库..."
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo $INSTALL_CMD docker-ce docker-ce-cli containerd.io
        fi
    else
        # 其他系统使用官方脚本
        log_info "使用Docker官方安装脚本..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
    fi
    
    # 启动Docker服务
    log_info "启动Docker服务..."
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 添加用户到docker组
    log_info "添加用户到docker组..."
    sudo usermod -aG docker $USER
    
    # 验证安装
    DOCKER_VERSION=$(docker --version)
    log_success "Docker安装完成: $DOCKER_VERSION"
else
    log_info "Docker已存在，跳过安装"
fi

# 安装Docker Compose
log_info "检查Docker Compose安装状态..."
if ! command -v docker-compose &> /dev/null; then
    log_info "开始安装Docker Compose..."
    
    # 获取最新版本号
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
    if [ -z "$COMPOSE_VERSION" ]; then
        COMPOSE_VERSION="v2.20.2"
        log_warning "无法获取最新版本，使用默认版本: $COMPOSE_VERSION"
    else
        log_info "获取到最新版本: $COMPOSE_VERSION"
    fi
    
    # 下载Docker Compose
    log_info "下载Docker Compose $COMPOSE_VERSION..."
    if curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /tmp/docker-compose; then
        sudo mv /tmp/docker-compose /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # 验证安装
        COMPOSE_VER=$(docker-compose --version)
        log_success "Docker Compose安装完成: $COMPOSE_VER"
    else
        log_warning "GitHub下载失败，尝试使用pip安装..."
        sudo $INSTALL_CMD python3-pip
        sudo pip3 install docker-compose
        log_success "Docker Compose通过pip安装完成"
    fi
else
    COMPOSE_VER=$(docker-compose --version)
    log_info "Docker Compose已安装: $COMPOSE_VER"
fi

# 安装Nginx（反向代理）
log_info "检查Nginx安装状态..."
if ! command -v nginx &> /dev/null; then
    log_info "开始安装Nginx..."
    sudo $INSTALL_CMD nginx
    
    # 启动Nginx服务
    log_info "启动Nginx服务..."
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # 验证安装
    NGINX_VERSION=$(nginx -v 2>&1)
    log_success "Nginx安装完成: $NGINX_VERSION"
else
    NGINX_VERSION=$(nginx -v 2>&1)
    log_info "Nginx已安装: $NGINX_VERSION"
    
    # 确保服务运行
    if ! systemctl is-active --quiet nginx; then
        log_info "启动Nginx服务..."
        sudo systemctl start nginx
        sudo systemctl enable nginx
    fi
fi

# 安装Certbot（SSL证书）
log_info "检查Certbot安装状态..."
if ! command -v certbot &> /dev/null; then
    log_info "开始安装Certbot..."
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        sudo $INSTALL_CMD certbot python3-certbot-nginx
    elif [ "$PACKAGE_MANAGER" = "yum" ]; then
        # 阿里云Linux需要先安装EPEL
        sudo $INSTALL_CMD epel-release
        sudo $INSTALL_CMD certbot python3-certbot-nginx
    else
        # CentOS/RHEL
        sudo $INSTALL_CMD epel-release
        sudo $INSTALL_CMD certbot python3-certbot-nginx
    fi
    
    CERTBOT_VERSION=$(certbot --version)
    log_success "Certbot安装完成: $CERTBOT_VERSION"
else
    CERTBOT_VERSION=$(certbot --version)
    log_info "Certbot已安装: $CERTBOT_VERSION"
fi

# 安装Git
log_info "检查Git安装状态..."
if ! command -v git &> /dev/null; then
    log_info "开始安装Git..."
    sudo $INSTALL_CMD git
    
    GIT_VERSION=$(git --version)
    log_success "Git安装完成: $GIT_VERSION"
else
    GIT_VERSION=$(git --version)
    log_info "Git已安装: $GIT_VERSION"
fi

# 配置防火墙
log_info "配置防火墙..."
if [ "$PACKAGE_MANAGER" = "apt" ]; then
    # Ubuntu/Debian 使用 ufw
    if command -v ufw &> /dev/null; then
        log_info "配置UFW防火墙..."
        sudo ufw --force enable
        sudo ufw allow ssh
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # 显示防火墙状态
        log_info "当前防火墙规则："
        sudo ufw status numbered
        log_success "UFW防火墙配置完成"
    fi
else
    # CentOS/RHEL 使用 firewalld
    if command -v firewall-cmd &> /dev/null; then
        log_info "配置Firewalld防火墙..."
        sudo systemctl start firewalld
        sudo systemctl enable firewalld
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --reload
        
        # 显示防火墙状态
        log_info "当前防火墙规则："
        sudo firewall-cmd --list-all
        log_success "Firewalld防火墙配置完成"
    fi
fi

# 验证所有安装
log_info "验证所有组件安装..."
echo ""
echo -e "${BLUE}📋 安装组件验证报告：${NC}"

# Docker验证
if command -v docker &> /dev/null && systemctl is-active --quiet docker; then
    log_success "Docker: $(docker --version) - 服务运行中"
else
    log_error "Docker: 安装失败或服务未运行"
fi

# Docker Compose验证
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose: $(docker-compose --version)"
else
    log_error "Docker Compose: 安装失败"
fi

# Nginx验证
if command -v nginx &> /dev/null && systemctl is-active --quiet nginx; then
    log_success "Nginx: $(nginx -v 2>&1) - 服务运行中"
else
    log_error "Nginx: 安装失败或服务未运行"
fi

# Certbot验证
if command -v certbot &> /dev/null; then
    log_success "Certbot: $(certbot --version)"
else
    log_error "Certbot: 安装失败"
fi

# Git验证
if command -v git &> /dev/null; then
    log_success "Git: $(git --version)"
else
    log_error "Git: 安装失败"
fi

echo ""
echo -e "${GREEN}🎉 服务器环境安装完成！${NC}"
echo ""
echo -e "${YELLOW}📝 重要提示：${NC}"
echo -e "${YELLOW}   1. 需要重新登录SSH以使Docker权限生效${NC}"
echo -e "${YELLOW}   2. 重新登录后可以运行以下命令部署应用：${NC}"
echo -e "${BLUE}      curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash${NC}"
echo ""
echo -e "${BLUE}🔍 已安装的组件：${NC}"
echo -e "${GREEN}   ✅ Docker & Docker Compose${NC}"
echo -e "${GREEN}   ✅ Nginx Web服务器${NC}"
echo -e "${GREEN}   ✅ Certbot SSL证书工具${NC}"
echo -e "${GREEN}   ✅ Git版本控制${NC}"
echo -e "${GREEN}   ✅ 防火墙配置${NC}"
echo ""
echo -e "${YELLOW}🚪 请现在执行以下命令：${NC}"
echo -e "${BLUE}   exit${NC}"
echo -e "${YELLOW}   然后重新登录SSH...${NC}"
