#!/bin/bash

# Open WebUI 生产环境启动脚本（不使用 Docker）
# 使用已安装的 Python 环境运行

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查前端是否已构建
if [ ! -d "build" ]; then
    echo "📦 构建前端..."
    npm run build
fi

# 设置环境变量
export PORT=3000
export HOST=0.0.0.0
export OPENAI_API_KEY="${OPENAI_API_KEY:-your_secret_key}"

# 提示用户设置 API Key
if [ "$OPENAI_API_KEY" = "your_secret_key" ]; then
    echo "⚠️  警告: 请设置 OPENAI_API_KEY 环境变量"
    echo "   例如: export OPENAI_API_KEY=sk-..."
    echo ""
fi

echo "🚀 启动 Open WebUI..."
echo "   访问地址: http://localhost:3000"
echo "   按 Ctrl+C 停止服务"
echo ""

# 运行服务
cd backend
python -m uvicorn open_webui.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --forwarded-allow-ips '*' \
    --workers 1

