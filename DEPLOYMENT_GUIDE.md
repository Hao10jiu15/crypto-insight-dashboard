# 🚀 Crypto Insight Dashboard 完整部署指南

## 📋 当前状态分析

根据您之前的部署尝试，您已经完成了环境安装，但在 Django 密钥生成步骤遇到了问题。现在我们已经修复了部署脚本，可以继续完成部署。

## 🔧 修复内容

已修复的问题：

1. ✅ Django 密钥生成不再依赖 Django 模块
2. ✅ 自动检测服务器 IP 并更新配置
3. ✅ 自动更新 nginx 和前端配置
4. ✅ 简化配置文件处理流程

## 🚀 接下来的部署步骤

### 步骤 1: 清理当前状态

```bash
# 连接到您的服务器
ssh admin@your-server-ip

# 清理之前的部署尝试
sudo rm -rf /opt/crypto-prediction
docker system prune -af
```

### 步骤 2: 重新运行修复后的部署脚本

```bash
# 运行修复后的部署脚本
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/deploy_from_github.sh | bash
```

### 步骤 3: 监控部署过程

部署过程中请关注以下关键步骤：

1. **环境检查** ✅ (已完成)

   - Docker、Git、docker-compose 已安装

2. **代码下载** 🔄

   - 从 GitHub 克隆最新代码

3. **配置生成** 🔄

   - 自动生成 Django 密钥
   - 自动更新服务器 IP 配置

4. **服务构建** 🔄

   - 构建 Docker 镜像
   - 启动所有服务

5. **数据库初始化** 🔄

   - 运行数据库迁移
   - 创建管理员用户

6. **健康检查** 🔄
   - 验证前后端服务

## 📊 预期输出示例

成功部署后，您应该看到类似输出：

```
🎉 部署完成！

📋 部署信息：
   📂 部署目录: /opt/crypto-prediction
   🌐 网站地址: http://your-server-ip
   🔧 管理后台: http://your-server-ip/admin
   👤 管理员账号: admin / admin123456
```

## 🔍 部署验证步骤

### 1. 检查服务状态

```bash
cd /opt/crypto-prediction
docker-compose -f docker-compose.prod.yml ps
```

期望输出：所有服务状态为 "Up"

### 2. 检查服务日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs nginx
```

### 3. 测试网站访问

```bash
# 测试API接口
curl http://localhost/api/currencies/

# 测试前端页面
curl -I http://localhost/
```

### 4. 访问管理后台

在浏览器中访问：`http://your-server-ip/admin`

- 用户名：`admin`
- 密码：`admin123456`

## 🛠️ 如果部署失败的排错步骤

### 1. Django 密钥生成失败

如果仍然遇到 Django 相关错误：

```bash
cd /opt/crypto-prediction
# 手动生成密钥
python3 -c "import secrets; import string; chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'; print(''.join(secrets.choice(chars) for i in range(50)))"
# 复制输出的密钥，然后编辑配置文件
nano .env.production
# 找到DJANGO_SECRET_KEY行，替换为生成的密钥
```

### 2. 服务启动失败

```bash
# 检查具体错误
docker-compose -f docker-compose.prod.yml logs backend

# 常见问题：端口被占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :5432

# 杀死占用端口的进程
sudo fuser -k 80/tcp
```

### 3. 网络访问问题

```bash
# 检查防火墙设置
sudo ufw status

# 确保端口开放
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 检查nginx状态
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

## 🔧 部署后配置

### 1. 修改管理员密码

```bash
cd /opt/crypto-prediction
docker-compose -f docker-compose.prod.yml exec backend python manage.py changepassword admin
```

### 2. 初始化货币数据

```bash
# 添加默认支持的加密货币
docker-compose -f docker-compose.prod.yml exec backend python manage.py init_currencies

# 手动添加特定货币
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
>>> from market_data.models import Currency
>>> Currency.objects.create(symbol='BTC', name='Bitcoin', coingecko_id='bitcoin')
>>> Currency.objects.create(symbol='ETH', name='Ethereum', coingecko_id='ethereum')
```

### 3. 获取初始数据

```bash
# 获取市场数据
docker-compose -f docker-compose.prod.yml exec backend python manage.py fetch_market_data

# 训练预测模型
docker-compose -f docker-compose.prod.yml exec backend python manage.py train_models
```

## 📈 常用管理命令

### 使用管理脚本

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

### 手动命令

```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 查看资源使用
docker stats

# 进入backend容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 运行Django命令
docker-compose -f docker-compose.prod.yml exec backend python manage.py <command>
```

## 🔒 安全配置

### 1. SSL 证书配置（可选）

```bash
# 如果有域名，可以申请SSL证书
sudo certbot --nginx -d yourdomain.com

# 或使用管理脚本
./deployment/manage.sh ssl
```

### 2. 防火墙配置

```bash
# 查看当前规则
sudo ufw status

# 仅允许必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📊 监控和维护

### 1. 设置定时任务

```bash
# 编辑crontab
crontab -e

# 添加以下行（每小时获取一次数据）
0 * * * * cd /opt/crypto-prediction && docker-compose -f docker-compose.prod.yml exec -T backend python manage.py fetch_market_data

# 每天凌晨3点训练模型
0 3 * * * cd /opt/crypto-prediction && docker-compose -f docker-compose.prod.yml exec -T backend python manage.py train_models
```

### 2. 日志轮转

```bash
# 配置Docker日志轮转（在docker-compose.yml中已配置）
# 手动清理日志
docker system prune -f
```

## 🎯 下一步操作

1. ✅ 运行修复后的部署脚本
2. ✅ 验证部署成功
3. ✅ 访问网站确认功能
4. ✅ 登录管理后台
5. ✅ 修改默认密码
6. ✅ 初始化货币数据
7. ✅ 设置定时任务
8. ✅ 配置监控和备份

## 📞 获取帮助

如果遇到问题：

1. 查看部署日志找到具体错误
2. 检查系统资源（内存、磁盘空间）
3. 查看项目 GitHub Issues
4. 提供错误日志和系统信息寻求帮助

---

🚀 **准备开始！运行修复后的部署脚本即可自动完成所有配置。**
