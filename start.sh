#!/usr/bin/env bash
set -e

echo "=== K8s Manager 一键启动 ==="

# Start MySQL + Backend + Frontend
echo ">>> 启动 Docker 服务 (MySQL + Backend + Frontend)..."
docker-compose up -d

echo ""
echo ">>> 服务地址:"
echo "    前端:  http://localhost:3000"
echo "    后端 API 文档: http://localhost:8000/docs"
echo "    MySQL: localhost:3306 (root / root123)"
echo ""
echo ">>> 查看日志: docker-compose logs -f"
echo ">>> 停止服务: docker-compose down"
