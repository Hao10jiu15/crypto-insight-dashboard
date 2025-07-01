#!/bin/bash
# 服务器环境安装脚本

echo "🚀 开始安装服务器环境..."

# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装Nginx（反向代理）
sudo apt install nginx -y

# 安装Certbot（SSL证书）
sudo apt install certbot python3-certbot-nginx -y

# 安装Git
sudo apt install git -y

echo "✅ 服务器环境安装完成！"
echo "📝 请注意：需要重新登录以使Docker权限生效"
