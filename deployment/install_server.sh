#!/bin/bash
# 服务器环境安装脚本 - 支持Ubuntu/Debian和CentOS/RHEL

set -e  # 遇到错误立即退出

echo "🚀 开始安装服务器环境..."

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
            ;;
        *"CentOS"*|*"Red Hat"*|*"Rocky"*|*"AlmaLinux"*)
            PACKAGE_MANAGER="dnf"
            INSTALL_CMD="dnf install -y"
            UPDATE_CMD="dnf update -y"
            ;;
        *)
            echo "❌ 不支持的操作系统: $OS"
            exit 1
            ;;
    esac
    
    echo "✅ 检测到操作系统: $OS"
    echo "📦 使用包管理器: $PACKAGE_MANAGER"
}

detect_os

# 更新系统包
echo "📦 更新系统包..."
sudo $UPDATE_CMD

# 安装Docker
echo "🐳 安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "✅ Docker安装完成"
else
    echo "ℹ️  Docker已安装"
fi

# 安装Docker Compose
echo "🔧 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose安装完成"
else
    echo "ℹ️  Docker Compose已安装"
fi

# 安装Nginx（反向代理）
echo "🌐 安装Nginx..."
if ! command -v nginx &> /dev/null; then
    sudo $INSTALL_CMD nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    echo "✅ Nginx安装完成"
else
    echo "ℹ️  Nginx已安装"
fi

# 安装Certbot（SSL证书）
echo "🔒 安装Certbot..."
if ! command -v certbot &> /dev/null; then
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        sudo $INSTALL_CMD certbot python3-certbot-nginx
    else
        sudo $INSTALL_CMD certbot python3-certbot-nginx
        # CentOS可能需要EPEL仓库
        sudo dnf install -y epel-release
        sudo dnf install -y certbot python3-certbot-nginx
    fi
    echo "✅ Certbot安装完成"
else
    echo "ℹ️  Certbot已安装"
fi

# 安装Git
echo "📋 安装Git..."
if ! command -v git &> /dev/null; then
    sudo $INSTALL_CMD git
    echo "✅ Git安装完成"
else
    echo "ℹ️  Git已安装"
fi

# 配置防火墙
echo "🔥 配置防火墙..."
if [ "$PACKAGE_MANAGER" = "apt" ]; then
    # Ubuntu/Debian 使用 ufw
    if command -v ufw &> /dev/null; then
        sudo ufw --force enable
        sudo ufw allow ssh
        sudo ufw allow 80
        sudo ufw allow 443
        echo "✅ UFW防火墙配置完成"
    fi
else
    # CentOS/RHEL 使用 firewalld
    if command -v firewall-cmd &> /dev/null; then
        sudo systemctl start firewalld
        sudo systemctl enable firewalld
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --reload
        echo "✅ Firewalld防火墙配置完成"
    fi
fi

echo ""
echo "🎉 服务器环境安装完成！"
echo ""
echo "📝 重要提示："
echo "   1. 需要重新登录SSH以使Docker权限生效"
echo "   2. 重新登录后可以运行以下命令部署应用："
echo "      curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash"
echo ""
echo "🔍 安装的组件："
echo "   ✅ Docker & Docker Compose"
echo "   ✅ Nginx Web服务器"
echo "   ✅ Certbot SSL证书工具"
echo "   ✅ Git版本控制"
echo "   ✅ 防火墙配置"
echo ""
echo "🚪 请现在退出并重新登录SSH..."
