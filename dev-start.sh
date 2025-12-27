#!/bin/bash

# Open WebUI 开发环境启动脚本
# 这个脚本会同时启动前端和后端开发服务器

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 虚拟环境不存在，请先运行: python3.12 -m venv venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 Node.js 依赖
if [ ! -d "node_modules" ]; then
    echo "❌ 错误: 前端依赖未安装，请先运行: npm install --legacy-peer-deps --engine-strict=false"
    exit 1
fi

echo "🚀 启动 Open WebUI 开发环境..."
echo ""
echo "📝 提示:"
echo "  - 前端开发服务器: http://localhost:5173"
echo "  - 后端 API 服务器: http://localhost:8080"
echo "  - 按 Ctrl+C 停止所有服务"
echo ""

# 设置环境变量
export CORS_ALLOW_ORIGIN="http://localhost:5173;http://localhost:8080"

# 设置系统库路径（用于 libgobject 等）
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export LD_LIBRARY_PATH="/opt/homebrew/lib:$LD_LIBRARY_PATH"

# 在后台启动后端开发服务器
echo "🔧 启动后端开发服务器 (端口 8080)..."
cd backend
python -m uvicorn open_webui.main:app --port 8080 --host 0.0.0.0 --forwarded-allow-ips '*' --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端开发服务器
echo "🎨 启动前端开发服务器 (端口 5173)..."
npm run dev &
FRONTEND_PID=$!

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 等待进程
wait

