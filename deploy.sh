#!/bin/bash

# Open WebUI 生产环境部署脚本
# 用于部署到 topify.ai 或其他 Web 平台

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

echo "🚀 Open WebUI 生产环境部署脚本"
echo "================================"
echo ""

# 检查参数
DEPLOY_METHOD=${1:-docker}
DOMAIN=${2:-topify.ai}

echo "部署方式: $DEPLOY_METHOD"
echo "域名: $DOMAIN"
echo ""

# 生成密钥
generate_secret_key() {
    if command -v openssl &> /dev/null; then
        openssl rand -base64 32
    else
        head -c 32 /dev/urandom | base64
    fi
}

case $DEPLOY_METHOD in
    docker)
        echo "📦 使用 Docker 部署..."
        
        # 检查 Docker
        if ! command -v docker &> /dev/null; then
            echo "❌ 错误: 未安装 Docker"
            exit 1
        fi
        
        # 构建镜像
        echo "🔨 构建 Docker 镜像..."
        docker build -t open-webui:latest .
        
        # 停止旧容器
        if docker ps -a | grep -q open-webui; then
            echo "🛑 停止旧容器..."
            docker stop open-webui 2>/dev/null || true
            docker rm open-webui 2>/dev/null || true
        fi
        
        # 创建数据卷（如果不存在）
        if ! docker volume ls | grep -q open-webui-data; then
            echo "📁 创建数据卷..."
            docker volume create open-webui-data
        fi
        
        # 生成密钥
        SECRET_KEY=$(generate_secret_key)
        
        # 运行容器
        echo "🚀 启动容器..."
        docker run -d \
            --name open-webui \
            -p 8080:8080 \
            -v open-webui-data:/app/backend/data \
            -e WEBUI_SECRET_KEY="$SECRET_KEY" \
            -e WEBUI_URL="https://$DOMAIN" \
            -e CORS_ALLOW_ORIGIN="https://$DOMAIN,https://www.$DOMAIN" \
            --restart unless-stopped \
            open-webui:latest
        
        echo "✅ Docker 部署完成！"
        echo "   访问地址: http://localhost:8080"
        echo "   数据卷: open-webui-data"
        ;;
    
    python)
        echo "🐍 使用 Python 部署..."
        
        # 检查 Python
        if ! command -v python3.12 &> /dev/null && ! command -v python3 &> /dev/null; then
            echo "❌ 错误: 未找到 Python 3.12"
            exit 1
        fi
        
        PYTHON_CMD=$(command -v python3.12 || command -v python3)
        
        # 创建虚拟环境
        if [ ! -d "venv" ]; then
            echo "📦 创建虚拟环境..."
            $PYTHON_CMD -m venv venv
        fi
        
        # 激活虚拟环境
        source venv/bin/activate
        
        # 安装依赖
        echo "📥 安装 Python 依赖..."
        pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install gunicorn
        
        # 构建前端
        if [ ! -d "build" ]; then
            echo "🎨 构建前端..."
            npm install --legacy-peer-deps --engine-strict=false
            npm run build
        fi
        
        # 安装项目
        pip install -e .
        
        # 生成密钥
        SECRET_KEY=$(generate_secret_key)
        
        # 创建 .env 文件
        cat > .env << EOF
WEBUI_SECRET_KEY=$SECRET_KEY
WEBUI_URL=https://$DOMAIN
CORS_ALLOW_ORIGIN=https://$DOMAIN,https://www.$DOMAIN
PORT=8080
HOST=0.0.0.0
EOF
        
        echo "✅ Python 环境准备完成！"
        echo ""
        echo "启动命令:"
        echo "  source venv/bin/activate"
        echo "  gunicorn open_webui.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080"
        ;;
    
    systemd)
        echo "⚙️  创建 Systemd 服务..."
        
        # 检查是否以 root 运行
        if [ "$EUID" -ne 0 ]; then
            echo "❌ 错误: 需要 root 权限创建 systemd 服务"
            exit 1
        fi
        
        # 生成密钥
        SECRET_KEY=$(generate_secret_key)
        
        # 创建服务文件
        SERVICE_FILE="/etc/systemd/system/open-webui.service"
        cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Open WebUI
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
Environment="WEBUI_SECRET_KEY=$SECRET_KEY"
Environment="WEBUI_URL=https://$DOMAIN"
Environment="CORS_ALLOW_ORIGIN=https://$DOMAIN,https://www.$DOMAIN"
ExecStart=$SCRIPT_DIR/venv/bin/gunicorn open_webui.main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:8080 \\
    --timeout 120 \\
    --access-logfile - \\
    --error-logfile -
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        # 重新加载 systemd
        systemctl daemon-reload
        systemctl enable open-webui
        systemctl start open-webui
        
        echo "✅ Systemd 服务创建完成！"
        echo "   查看状态: systemctl status open-webui"
        echo "   查看日志: journalctl -u open-webui -f"
        ;;
    
    *)
        echo "❌ 未知的部署方式: $DEPLOY_METHOD"
        echo ""
        echo "用法: $0 [docker|python|systemd] [域名]"
        echo ""
        echo "示例:"
        echo "  $0 docker topify.ai"
        echo "  $0 python topify.ai"
        echo "  $0 systemd topify.ai"
        exit 1
        ;;
esac

echo ""
echo "📝 下一步:"
echo "  1. 配置反向代理 (Nginx/Apache)"
echo "  2. 配置 SSL 证书 (Let's Encrypt)"
echo "  3. 配置防火墙规则"
echo "  4. 访问 https://$DOMAIN 测试"
echo ""
echo "📚 详细文档请查看 DEPLOY.md"

