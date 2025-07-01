# 🚀 生产环境部署指南

## 📋 部署前准备

### 1. 服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **内存**: 最少 2GB，推荐 4GB+
- **存储**: 最少 20GB 可用空间
- **CPU**: 2 核心以上
- **网络**: 稳定的网络连接

### 2. 域名配置

- 购买域名并配置 DNS 解析到您的服务器 IP
- 确保域名可以正常访问

## 🛠️ 部署步骤

### 步骤 1: 登录服务器并安装环境

```bash
# 上传并运行环境安装脚本
chmod +x deployment/install_server.sh
./deployment/install_server.sh

# 重新登录使Docker权限生效
exit
# 重新ssh登录
```

### 步骤 2: 上传项目代码

```bash
# 方法1: 使用Git克隆
git clone https://github.com/yourusername/crypto-insight-dashboard.git
cd crypto-insight-dashboard

# 方法2: 使用scp上传
# 在本地执行
scp -r crypto-insight-dashboard user@your-server-ip:/home/user/
```

### 步骤 3: 配置环境变量

```bash
# 复制并编辑生产环境配置
cp .env.production.example .env.production
nano .env.production

# 修改以下重要配置:
# - DB_PASSWORD: 数据库密码
# - DJANGO_SECRET_KEY: Django密钥
# - DJANGO_ALLOWED_HOSTS: 您的域名
# - 邮件配置（用于错误通知）
```

### 步骤 4: 更新配置文件中的域名

```bash
# 更新nginx配置
nano deployment/nginx.conf
# 将 yourdomain.com 替换为您的实际域名

# 更新前端API配置
nano frontend/Dockerfile.prod
# 将 yourdomain.com 替换为您的实际域名
```

### 步骤 5: 执行部署

```bash
# 给部署脚本执行权限
chmod +x deployment/deploy.sh

# 执行部署
./deployment/deploy.sh
```

### 步骤 6: 配置 SSL 证书

```bash
# 申请免费SSL证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 日常维护

### 常用维护命令

```bash
# 给维护脚本执行权限
chmod +x deployment/manage.sh

# 查看服务状态
./deployment/manage.sh status

# 查看日志
./deployment/manage.sh logs

# 重启服务
./deployment/manage.sh restart

# 备份数据库
./deployment/manage.sh backup

# 更新应用
./deployment/manage.sh update
```

### 监控和日志

```bash
# 查看实时日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx

# 查看系统资源使用
docker stats

# 查看磁盘使用
df -h
```

## 🔒 安全配置

### 1. 防火墙设置

```bash
# 安装ufw
sudo apt install ufw

# 配置防火墙规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
```

### 2. 修改默认密码

访问 `https://yourdomain.com/admin` 并：

1. 使用默认账号 `admin/admin123456` 登录
2. 修改管理员密码
3. 创建新的管理员账号
4. 删除默认账号

### 3. 定期更新

```bash
# 每周更新系统
sudo apt update && sudo apt upgrade -y

# 每月更新应用
./deployment/manage.sh update
```

## 📊 性能优化

### 1. 数据库优化

```bash
# 连接到数据库容器
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d crypto_prediction_db

# 创建索引（如果需要）
CREATE INDEX IF NOT EXISTS idx_market_data_time ON market_data_marketdata(time);
CREATE INDEX IF NOT EXISTS idx_predictions_time ON market_data_priceprediction(time);
```

### 2. 缓存优化

```bash
# 查看Redis缓存状态
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory
```

## 🆘 故障排除

### 常见问题解决

#### 1. 服务无法启动

```bash
# 查看详细错误日志
docker-compose -f docker-compose.prod.yml logs

# 检查端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# 重置数据库（谨慎操作）
docker-compose -f docker-compose.prod.yml down
docker volume rm crypto-insight-dashboard_postgres_data_prod
./deployment/deploy.sh
```

#### 3. SSL 证书问题

```bash
# 重新申请证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com --force-renewal

# 检查证书状态
sudo certbot certificates
```

#### 4. 应用内存不足

```bash
# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 📞 技术支持

如果遇到问题，请：

1. 检查日志文件
2. 查看 GitHub Issues
3. 联系技术支持

## 📈 监控建议

建议安装以下监控工具：

- **Portainer**: Docker 容器管理界面
- **Grafana + Prometheus**: 系统监控
- **Uptime Robot**: 网站可用性监控

---

## 🎉 部署完成！

恭喜！您的加密货币预测系统现在已经在生产环境中运行了。

**访问地址:**

- 🌐 主网站: https://yourdomain.com
- 🔧 管理后台: https://yourdomain.com/admin

记得定期备份数据并保持系统更新！
