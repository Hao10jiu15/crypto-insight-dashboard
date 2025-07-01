# GitHub 仓库设置指南

## 第一步：创建 GitHub 仓库

1. 访问 [GitHub](https://github.com) 并登录
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - Repository name: `crypto-insight-dashboard`
   - Description: `Cryptocurrency price prediction system with Django backend and Vue frontend`
   - 选择 Public 或 Private（根据需要）
   - **不要**勾选 "Initialize this repository with a README"
   - **不要**添加 .gitignore 或 license（我们已经有了）

4. 点击 "Create repository"

## 第二步：连接本地仓库到 GitHub

复制 GitHub 提供的仓库 URL，然后在项目根目录执行：

```bash
# 添加远程仓库（替换为你的实际仓库URL）
git remote add origin https://github.com/Hao10jiu15/crypto-insight-dashboard.git

# 推送代码到 GitHub
git push -u origin master
```

## 第三步：验证推送成功

刷新 GitHub 仓库页面，确认所有文件都已上传。

## 接下来的部署步骤

一旦代码推送到 GitHub，你就可以：

1. 在服务器上使用 `deployment/deploy_from_github.sh` 脚本进行自动化部署
2. 配置你的域名和 SSL 证书
3. 设置定时任务和监控

## 注意事项

- 确保 `.env` 文件没有被提交（已在 .gitignore 中排除）
- 生产环境的敏感信息应该在服务器上单独配置
- 定期备份数据库和模型文件

## 示例命令（请替换为实际的 GitHub 仓库 URL）

```bash
# 如果你的 GitHub 用户名是 myusername
git remote add origin https://github.com/myusername/crypto-insight-dashboard.git
git push -u origin master
```
