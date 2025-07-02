# 🚀 服务器部署快速指南

## 🎯 一键部署流程

####### 阿里云 Linux (Alibaba Cloud Linux) 系统：

```bash
# 第一步：安装必要工具
sudo yum update -y
sudo yum install curl git -y

# 第二步：下载并运行环境安装脚本
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_server.sh | bash
```

#### Ubuntu 22.04 (推荐) 系统：

```bash
# 方法1：使用优化的Ubuntu安装脚本 (推荐)
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_ubuntu.sh | bash

# 方法2：使用通用安装脚本
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_server.sh | bash
```

您需要一台具备以下配置的 Linux 服务器：

- **操作系统**: Ubuntu 20.04+ 或 CentOS 8+ 或 Alibaba Cloud Linux
- **内存**: 最少 2GB（推荐 4GB+）
- **存储**: 至少 20GB 可用空间
- **网络**: 稳定的公网连接

### 2. 在服务器上执行以下命令

#### Ubuntu/Debian 系统：

```bash
# 第一步：安装必要工具
sudo apt update && sudo apt upgrade -y
sudo apt install curl git -y

# 第二步：下载并运行环境安装脚本
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_server.sh | bash
```

#### CentOS/RHEL 系统：

```bash
# 第一步：安装必要工具
sudo dnf update -y
sudo dnf install curl git -y

# 第二步：下载并运行环境安装脚本
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_server.sh | bash
```

#### 阿里云 Linux (Alibaba Cloud Linux) 系统：

```bash
# 第一步：安装必要工具
sudo yum update -y
sudo yum install curl git -y

# 第二步：下载并运行环境安装脚本
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_server.sh | bash
```

# 重新登录使 Docker 权限生效

exit

# 重新 SSH 登录

# 第三步：克隆项目并部署

curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash

````

### 3. 配置域名（重要）

部署脚本会提示您配置以下文件：

1. **编辑生产环境配置**:

   ```bash
   nano /opt/crypto-prediction/.env.production
````

主要修改：

- `DJANGO_ALLOWED_HOSTS`: 改为您的域名
- `DB_PASSWORD`: 设置安全的数据库密码

2. **更新 Nginx 配置**:

   ```bash
   nano /opt/crypto-prediction/deployment/nginx.conf
   ```

   将所有 `yourdomain.com` 替换为您的实际域名

3. **更新前端 API 配置**:
   ```bash
   nano /opt/crypto-prediction/frontend/Dockerfile.prod
   ```
   将 API 地址改为您的域名

### 4. 申请 SSL 证书

```bash
cd /opt/crypto-prediction
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 5. 验证部署

```bash
cd /opt/crypto-prediction
./deployment/verify_deployment.sh
```

## 🌟 访问您的应用

部署完成后，您可以访问：

- **主网站**: `https://yourdomain.com`
- **管理后台**: `https://yourdomain.com/admin`
  - 默认账号: `admin`
  - 默认密码: `admin123456` （请立即修改）

## ⚡ 一键管理命令

```bash
cd /opt/crypto-prediction

# 查看服务状态
./deployment/manage.sh status

# 查看日志
./deployment/manage.sh logs

# 重启服务
./deployment/manage.sh restart

# 备份数据
./deployment/manage.sh backup

# 更新应用
./deployment/manage.sh update
```

## 🔧 首次使用配置

1. **登录管理后台** (`https://yourdomain.com/admin`)
2. **修改默认密码**
3. **添加货币**：点击 "添加默认货币"
4. **运行完整流程**：为每个货币点击 "⚡ 完整流程" 按钮

## 🆘 故障排除

### 常见问题

1. **服务无法启动**

   ```bash
   docker-compose -f docker-compose.prod.yml logs
   ```

2. **网站无法访问**

   ```bash
   # Ubuntu/Debian 系统：
   sudo ufw status  # 检查防火墙

   # CentOS/RHEL 系统：
   sudo firewall-cmd --list-ports  # 检查防火墙

   sudo systemctl status nginx  # 检查Nginx状态
   ```

3. **SSL 证书问题**

   ```bash
   sudo certbot certificates  # 查看证书状态
   ```

4. **数据库连接失败**
   ```bash
   docker exec -it crypto_postgres_prod psql -U postgres -d crypto_prediction_db
   ```

### 重新部署

如果需要重新部署：

```bash
cd /opt/crypto-prediction
git pull origin master
./deployment/manage.sh update
```

## 📈 性能监控

建议安装以下监控工具：

1. **系统监控**:

   #### Ubuntu/Debian 系统：

   ```bash
   sudo apt install htop iotop
   ```

   #### CentOS/RHEL 系统：

   ```bash
   sudo dnf install htop iotop
   ```

2. **Docker 监控**:

   ```bash
   docker stats
   ```

3. **磁盘监控**:
   ```bash
   df -h
   du -sh /opt/crypto-prediction
   ```

## 🔒 安全建议

1. **防火墙配置**:

   #### Ubuntu/Debian 系统：

   ````bash
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   ```   #### CentOS/RHEL/阿里云Linux 系统：
   ```bash
   sudo systemctl start firewalld
   sudo systemctl enable firewalld
   sudo firewall-cmd --permanent --add-service=ssh
   sudo firewall-cmd --permanent --add-port=80/tcp
   sudo firewall-cmd --permanent --add-port=443/tcp
   sudo firewall-cmd --reload
   ````

2. **定期更新**:

   #### Ubuntu/Debian 系统：

   ```bash
   # 每周执行
   sudo apt update && sudo apt upgrade -y
   ./deployment/manage.sh update
   ```

   #### CentOS/RHEL 系统：

   ```bash
   # 每周执行
   sudo dnf update -y
   ./deployment/manage.sh update
   ```

3. **备份策略**:
   ```bash
   # 设置定时备份
   crontab -e
   # 添加：0 2 * * * cd /opt/crypto-prediction && ./deployment/manage.sh backup
   ```

## 🎉 完成！

恭喜！您的加密货币预测系统现在已经在生产环境中运行了。

如果遇到任何问题，请查看：

- [完整部署文档](deployment/README.md)
- [GitHub Issues](https://github.com/Hao10jiu15/crypto-insight-dashboard/issues)

---

⭐ 记得给项目点个星！
