#!/bin/bash

# Open WebUI API Keys 配置脚本
# 用于更新运行中的容器或重新启动容器以添加 API Keys

set -e

echo "🔑 Open WebUI API Keys 配置工具"
echo "================================"
echo ""

# 检查 Docker
DOCKER_CMD="/Applications/Docker.app/Contents/Resources/bin/docker"
if ! $DOCKER_CMD info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

# 读取 API Keys
echo "请输入 API Keys（留空跳过）："
echo ""

read -p "OpenAI API Key (sk-...): " OPENAI_KEY
read -p "Google Gemini API Key: " GEMINI_KEY

# 构建环境变量
ENV_ARGS=""

if [ -n "$OPENAI_KEY" ]; then
    ENV_ARGS="$ENV_ARGS -e OPENAI_API_KEY=$OPENAI_KEY"
    echo "✅ 已添加 OpenAI API Key"
fi

if [ -n "$GEMINI_KEY" ]; then
    ENV_ARGS="$ENV_ARGS -e GEMINI_API_KEY=$GEMINI_KEY"
    echo "✅ 已添加 Gemini API Key"
fi

if [ -z "$ENV_ARGS" ]; then
    echo ""
    echo "⚠️  未输入任何 API Key"
    echo "提示: 你也可以通过 Web UI 配置（Settings → Connections）"
    exit 0
fi

echo ""
echo "🔄 更新容器配置..."

# 停止并删除现有容器
if $DOCKER_CMD ps -a | grep -q "open-webui"; then
    echo "停止现有容器..."
    $DOCKER_CMD stop open-webui 2>/dev/null || true
    $DOCKER_CMD rm open-webui 2>/dev/null || true
fi

# 启动新容器
echo "启动新容器（已配置 API Keys）..."
$DOCKER_CMD run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  $ENV_ARGS \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main

echo ""
echo "✅ 容器已更新并启动！"
echo ""
echo "📝 说明:"
echo "   - API Keys 已保存到容器环境变量"
echo "   - 你也可以在 Web UI 中修改（Settings → Connections）"
echo "   - 访问: http://localhost:3000"
echo ""

sleep 3
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Open WebUI 服务正常运行"
else
    echo "⏳ 服务正在启动中..."
fi


