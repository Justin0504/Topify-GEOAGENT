#!/bin/bash
# 构建并运行自定义 Open WebUI

set -e

echo "🚀 开始构建自定义 Open WebUI..."

# 加载 nvm（如果存在）
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" || echo "⚠️  nvm 未找到，请确保 Node.js 22 已安装"

# 使用 Node.js 22
if command -v nvm &> /dev/null; then
    nvm use 22 2>/dev/null || echo "⚠️  请安装 Node.js 22"
fi

# 检查 Node.js 版本
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" != "22" ]; then
    echo "❌ 需要 Node.js 22，当前版本: $(node --version)"
    echo "请运行: nvm install 22 && nvm use 22"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"

# 停止并删除旧容器
echo "🛑 停止旧容器..."
docker stop open-webui 2>/dev/null || true
docker rm open-webui 2>/dev/null || true

# 构建镜像
echo "🔨 构建 Docker 镜像（这需要 10-20 分钟）..."
IMAGE_NAME="open-webui-custom:latest"

docker build \
  --build-arg NODE_OPTIONS="--max-old-space-size=4096" \
  -t $IMAGE_NAME \
  . 2>&1 | tee /tmp/docker_build.log

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "❌ 构建失败！查看日志: tail -50 /tmp/docker_build.log"
    exit 1
fi

echo "✅ 构建成功！"

# 运行容器
echo "🚀 启动容器..."
docker run -d \
  --name open-webui \
  --restart always \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  -v "$(pwd)/output:/app/backend/data/output" \
  $IMAGE_NAME

echo "✅ 完成！"
echo "🌐 访问地址: http://localhost:3000"
echo ""
echo "📋 查看日志: docker logs -f open-webui"
echo "🛑 停止容器: docker stop open-webui"


