# Open WebUI 部署到 Web 平台指南

## 🚀 部署方案

### 方案 1: Docker 部署（推荐）

这是最简单和可靠的部署方式，适合大多数云平台。

#### 1.1 构建 Docker 镜像

```bash
# 在项目根目录执行
docker build -t open-webui:latest .
```

#### 1.2 运行容器

```bash
docker run -d \
  -p 8080:8080 \
  -v open-webui-data:/app/backend/data \
  -e WEBUI_SECRET_KEY=$(openssl rand -base64 32) \
  -e OLLAMA_BASE_URL=http://your-ollama-server:11434 \
  --name open-webui \
  --restart unless-stopped \
  open-webui:latest
```

### 方案 2: 直接 Python 部署

适合已有 Python 环境的服务器。

#### 2.1 生产环境安装

```bash
# 1. 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 构建前端
npm install --legacy-peer-deps --engine-strict=false
npm run build

# 4. 安装项目
pip install -e .
```

#### 2.2 使用 Gunicorn 运行（生产环境推荐）

```bash
# 安装 gunicorn
pip install gunicorn

# 运行（多进程，适合生产环境）
gunicorn open_webui.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8080 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### 方案 3: 使用 Systemd 服务（Linux 服务器）

创建 systemd 服务文件，实现自动启动和管理。

## 📋 部署到 topify.ai 或其他平台的步骤

### 步骤 1: 准备部署文件

1. **构建前端**
   ```bash
   npm run build
   ```

2. **准备环境变量**
   创建 `.env` 文件：
   ```env
   WEBUI_SECRET_KEY=your-secret-key-here
   OLLAMA_BASE_URL=http://your-ollama-server:11434
   OPENAI_API_KEY=your-openai-key-if-needed
   PORT=8080
   HOST=0.0.0.0
   ```

### 步骤 2: 配置反向代理（Nginx）

如果使用自己的服务器，需要配置 Nginx：

```nginx
server {
    listen 80;
    server_name topify.ai www.topify.ai;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name topify.ai www.topify.ai;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # 增加上传文件大小限制
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # WebSocket 支持
    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 步骤 3: 配置 SSL 证书

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d topify.ai -d www.topify.ai
```

### 步骤 4: 配置防火墙

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 🔧 环境变量配置

### 必需的环境变量

- `WEBUI_SECRET_KEY`: 用于加密的密钥（自动生成或手动设置）
- `PORT`: 服务端口（默认 8080）

### 可选的环境变量

```env
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 配置
OPENAI_API_KEY=sk-...
OPENAI_API_BASE_URL=https://api.openai.com/v1

# 数据库配置
DATABASE_URL=sqlite:///./data/webui.db
# 或 PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/webui

# Redis 配置（用于会话管理）
REDIS_URL=redis://localhost:6379

# CORS 配置
CORS_ALLOW_ORIGIN=https://topify.ai,https://www.topify.ai

# 日志级别
GLOBAL_LOG_LEVEL=INFO

# 其他配置
WEBUI_URL=https://topify.ai
ENABLE_SIGNUP=false  # 禁用注册
ENABLE_LOGIN=true    # 启用登录
```

## 📦 平台特定部署

### Vercel / Netlify

这些平台主要支持静态网站，Open WebUI 需要后端 API，建议：

1. 前端部署到 Vercel/Netlify
2. 后端 API 部署到其他平台（如 Railway, Render, Fly.io）

### Railway / Render / Fly.io

这些平台支持 Docker 和 Python 应用：

1. **Railway**: 直接连接 GitHub，自动部署 Docker 容器
2. **Render**: 支持 Dockerfile 或直接运行 Python
3. **Fly.io**: 支持 Docker 部署，全球边缘网络

### AWS / GCP / Azure

使用云平台的容器服务：

- **AWS**: ECS, EKS, App Runner
- **GCP**: Cloud Run, GKE
- **Azure**: Container Instances, AKS

## 🛡️ 安全建议

1. **使用 HTTPS**: 必须配置 SSL 证书
2. **设置强密钥**: `WEBUI_SECRET_KEY` 使用强随机字符串
3. **限制访问**: 使用防火墙限制 IP 访问
4. **定期更新**: 保持 Docker 镜像和依赖更新
5. **备份数据**: 定期备份 `/app/backend/data` 目录

## 📊 监控和日志

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8080/health

# 应该返回: {"status":true}
```

### 查看日志

```bash
# Docker 日志
docker logs -f open-webui

# Systemd 日志
journalctl -u open-webui -f
```

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建
docker build -t open-webui:latest .

# 3. 停止旧容器
docker stop open-webui
docker rm open-webui

# 4. 启动新容器（使用相同的数据卷）
docker run -d \
  -p 8080:8080 \
  -v open-webui-data:/app/backend/data \
  --name open-webui \
  open-webui:latest
```

## 📝 常见问题

### Q: 如何配置自定义域名？

A: 在 DNS 提供商处添加 A 记录，指向服务器 IP，然后配置 Nginx。

### Q: 如何启用用户注册？

A: 设置环境变量 `ENABLE_SIGNUP=true`

### Q: 如何连接远程 Ollama 服务器？

A: 设置 `OLLAMA_BASE_URL=http://your-ollama-server:11434`

### Q: 如何备份数据？

A: 备份 Docker 卷：`docker run --rm -v open-webui-data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data`

## 🎯 快速部署脚本

查看 `deploy.sh` 脚本获取一键部署方案。


