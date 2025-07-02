# Docker 安装冲突修复说明

## 问题描述

在 Ubuntu 22.04 系统上安装 Docker 时出现 `containerd.io` 与系统已有的 `containerd` 包冲突的错误：

```
The following packages have unmet dependencies:
 containerd.io : Conflicts: containerd
E: Error, pkgProblemResolver::Resolve generated breaks, this may be caused by held packages.
```

## 修复内容

已修复以下部署脚本中的 Docker 安装问题：

### 1. `deployment/install_quick.sh`

- ✅ 修改 Docker 安装方式，使用官方 Docker 仓库
- ✅ 在安装前先移除冲突的包（`containerd` 和 `runc`）
- ✅ 更新 Docker Compose 验证逻辑，支持新的 `docker compose` 命令

### 2. `deployment/install_ubuntu_cn.sh`

- ✅ 增强包冲突处理，添加 `autoremove` 清理
- ✅ 更新 Docker Compose 安装逻辑，优先使用内置的 docker-compose-plugin
- ✅ 添加降级策略，如果 plugin 不可用则安装独立版本

### 3. `deployment/install_ubuntu.sh`

- ✅ 增强包冲突处理
- ✅ 重构 Docker Compose 安装逻辑，支持多种安装方式
- ✅ 优化验证流程

### 4. `deployment/install_server.sh`

- ✅ 在 Docker 安装前添加冲突包移除步骤
- ✅ 确保与其他脚本保持一致的处理方式

## 修复原理

1. **移除冲突包**: 在安装 Docker 官方包之前，先移除可能冲突的包：

   ```bash
   sudo apt remove -yq docker docker-engine docker.io containerd runc 2>/dev/null || true
   sudo apt autoremove -yq 2>/dev/null || true
   ```

2. **使用官方仓库**: 确保所有脚本都使用 Docker 官方仓库，避免与系统包冲突：

   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

3. **完整安装**: 安装完整的 Docker 套件，包括新的 docker-compose-plugin：
   ```bash
   sudo apt install -yq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

## 使用方法

现在可以重新运行快速安装脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/Hao10jiu15/crypto-insight-dashboard/master/deployment/install_quick.sh | bash
```

或者根据网络环境选择合适的脚本：

- 中国大陆用户: `install_ubuntu_cn.sh`
- 国际用户: `install_ubuntu.sh`
- 服务器环境: `install_server.sh`

## 验证安装

安装完成后，脚本会自动验证：

- Docker 版本
- Docker Compose 版本（支持 `docker compose` 和 `docker-compose` 两种命令）
- Docker 服务状态

如需手动验证：

```bash
docker --version
docker compose version  # 或 docker-compose --version
sudo systemctl status docker
```
