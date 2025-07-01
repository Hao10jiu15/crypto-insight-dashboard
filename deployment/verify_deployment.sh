#!/bin/bash
# 部署后验证脚本

set -e

echo "🔍 开始验证部署状态..."

DEPLOY_DIR="/opt/crypto-prediction"
DOMAIN="yourdomain.com"
API_URL="https://$DOMAIN/api"
FRONTEND_URL="https://$DOMAIN"

# 检查Docker容器状态
echo "📦 检查Docker容器状态..."
cd "$DEPLOY_DIR"

containers=(
    "crypto-prediction-backend"
    "crypto-prediction-frontend" 
    "crypto-prediction-redis"
    "crypto-prediction-postgres"
    "crypto-prediction-nginx"
)

for container in "${containers[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "$container"; then
        echo "✅ $container - 运行中"
    else
        echo "❌ $container - 未运行"
        docker logs "$container" --tail 20
    fi
done

# 检查端口监听
echo "🌐 检查端口监听..."
ports=(80 443 5432 6379)

for port in "${ports[@]}"; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "✅ 端口 $port - 监听中"
    else
        echo "❌ 端口 $port - 未监听"
    fi
done

# 检查SSL证书
echo "🔒 检查SSL证书..."
if [ -f "/opt/crypto-prediction/ssl/cert.pem" ]; then
    echo "✅ SSL证书文件存在"
    # 检查证书有效期
    openssl x509 -in "/opt/crypto-prediction/ssl/cert.pem" -noout -dates 2>/dev/null || echo "⚠️  证书格式可能有问题"
else
    echo "❌ SSL证书文件不存在"
fi

# 检查API端点
echo "🔌 检查API端点..."
api_endpoints=(
    "/api/currencies/"
    "/api/market-share/" 
    "/api/currency-metrics/"
    "/admin/"
)

for endpoint in "${api_endpoints[@]}"; do
    url="$API_URL$endpoint"
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -qE "^(200|302|401)$"; then
        echo "✅ $url - 可访问"
    else
        echo "❌ $url - 不可访问"
    fi
done

# 检查前端
echo "🖥️  检查前端..."
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200"; then
    echo "✅ 前端 - 可访问"
else
    echo "❌ 前端 - 不可访问"
fi

# 检查数据库连接
echo "🗄️  检查数据库连接..."
if docker exec crypto-prediction-backend python manage.py check --database default 2>/dev/null; then
    echo "✅ 数据库连接 - 正常"
else
    echo "❌ 数据库连接 - 异常"
fi

# 检查Redis连接
echo "🔄 检查Redis连接..."
if docker exec crypto-prediction-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis连接 - 正常"
else
    echo "❌ Redis连接 - 异常"
fi

# 检查定时任务
echo "⏰ 检查定时任务..."
if systemctl is-active --quiet crypto-prediction 2>/dev/null; then
    echo "✅ 系统服务 - 运行中"
else
    echo "❌ 系统服务 - 未运行"
    echo "请检查: sudo systemctl status crypto-prediction"
fi

# 检查日志错误
echo "📝 检查最近错误日志..."
echo "Backend错误："
docker logs crypto-prediction-backend --since="1h" 2>&1 | grep -i error | tail -5 || echo "无错误"

echo "Nginx错误："
docker logs crypto-prediction-nginx --since="1h" 2>&1 | grep -i error | tail -5 || echo "无错误"

# 性能检查
echo "⚡ 性能检查..."
echo "内存使用："
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep crypto-prediction

echo "磁盘使用："
df -h "$DEPLOY_DIR"

# 最终总结
echo ""
echo "🎯 验证完成！"
echo "如果有❌标记的项目，请检查相应的配置和日志。"
echo ""
echo "常用调试命令："
echo "- 查看容器日志: docker logs <容器名>"
echo "- 重启服务: sudo systemctl restart crypto-prediction"
echo "- 查看系统服务状态: sudo systemctl status crypto-prediction"
echo "- 进入容器调试: docker exec -it <容器名> /bin/bash"
echo ""
echo "Web界面："
echo "- 前端: $FRONTEND_URL"
echo "- Django Admin: $API_URL/admin/"
echo "- API文档: $API_URL/swagger/"
