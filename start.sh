#!/usr/bin/env bash
set -e

echo "=== K8s Manager 一键启动 ==="

echo ">>> 启动 Docker 服务 (Backend + Frontend)..."
docker-compose up -d

echo ""
echo ">>> 请确保已执行数据库初始化：mysql -u root -p < sql/init.sql"
echo ""
echo ">>> 服务地址:"
echo "    前端:  http://localhost:3000"
echo "    后端 API 文档: http://localhost:8000/docs"
echo ""
echo ">>> 查看日志: docker-compose logs -f"
echo ">>> 停止服务: docker-compose down"
