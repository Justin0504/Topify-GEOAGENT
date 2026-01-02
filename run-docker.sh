#!/bin/bash

# Open WebUI Docker 启动脚本
# 使用前请确保已安装并启动 Docker Desktop

set -e

echo "🐳 启动 Open WebUI Docker 容器..."
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误: Docker 未运行"
    echo "   请先启动 Docker Desktop"
    exit 1
fi

# 检查是否已有同名容器
if docker ps -a | grep -q "open-webui"; then
    echo "⚠️  发现已存在的 open-webui 容器"
    read -p "是否删除旧容器并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止并删除旧容器..."
        docker stop open-webui 2>/dev/null || true
        docker rm open-webui 2>/dev/null || true
    else
        echo "❌ 操作已取消"
        exit 1
    fi
fi

# 设置 API Key（如果未设置）
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  提示: 未设置 OPENAI_API_KEY 环境变量"
    echo "   可以在运行前设置: export OPENAI_API_KEY=sk-..."
    echo "   或稍后在 Web UI 中配置"
    echo ""
    OPENAI_API_KEY_VALUE=""
else
    OPENAI_API_KEY_VALUE="$OPENAI_API_KEY"
fi

# 运行容器
echo "🚀 启动容器..."
docker run -d \
    -p 3000:8080 \
    -e OPENAI_API_KEY="${OPENAI_API_KEY_VALUE}" \
    -v open-webui:/app/backend/data \
    --name open-webui \
    --restart always \
    ghcr.io/open-webui/open-webui:main

echo ""
echo "✅ 容器启动成功！"
echo ""
echo "📝 信息:"
echo "   - 访问地址: http://localhost:3000"
echo "   - 数据卷: open-webui"
echo "   - 容器名称: open-webui"
echo ""
echo "🔧 常用命令:"
echo "   查看日志: docker logs -f open-webui"
echo "   停止容器: docker stop open-webui"
echo "   启动容器: docker start open-webui"
echo "   删除容器: docker rm -f open-webui"
echo "   查看状态: docker ps | grep open-webui"
echo ""

# 等待几秒后检查状态
sleep 3
if docker ps | grep -q "open-webui"; then
    echo "✅ 容器运行正常"
else
    echo "⚠️  容器可能启动失败，查看日志: docker logs open-webui"
fi


