#!/bin/bash
# 生产环境维护脚本

case "$1" in
    start)
        echo "🚀 启动服务..."
        docker-compose -f docker-compose.prod.yml up -d
        ;;
    stop)
        echo "🛑 停止服务..."
        docker-compose -f docker-compose.prod.yml down
        ;;
    restart)
        echo "🔄 重启服务..."
        docker-compose -f docker-compose.prod.yml restart
        ;;
    status)
        echo "📊 服务状态："
        docker-compose -f docker-compose.prod.yml ps
        ;;
    logs)
        echo "📋 查看日志："
        docker-compose -f docker-compose.prod.yml logs -f --tail=100
        ;;
    backup)
        echo "💾 备份数据库..."
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U postgres crypto_prediction_db > "$BACKUP_FILE"
        echo "备份完成: $BACKUP_FILE"
        ;;
    update)
        echo "🔄 更新应用..."
        git pull
        docker-compose -f docker-compose.prod.yml build --no-cache
        docker-compose -f docker-compose.prod.yml up -d
        docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate
        docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput
        echo "更新完成"
        ;;
    ssl)
        echo "🔒 申请SSL证书..."
        sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|status|logs|backup|update|ssl}"
        echo ""
        echo "命令说明："
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看服务日志"
        echo "  backup  - 备份数据库"
        echo "  update  - 更新应用代码"
        echo "  ssl     - 申请SSL证书"
        exit 1
        ;;
esac
