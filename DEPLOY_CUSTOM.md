# 🚀 部署自定义 Open WebUI 完整指南

## 前置条件

- ✅ Node.js 22 (已通过 nvm 安装)
- ✅ Docker Desktop
- 📦 Docker Hub 账号 或 私有镜像仓库
- 🖥️ 目标服务器（VPS/云服务器）

---

## Step 1: 本地构建 Docker 镜像

### 1.1 确保使用正确的 Node.js 版本

```bash
# 加载 nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 使用 Node.js 22
nvm use 22
node --version  # 应该显示 v22.x.x
```

### 1.2 安装依赖

```bash
cd /Users/justin/Downloads/open-webui-main

# 清理旧依赖
rm -rf node_modules package-lock.json

# 安装依赖
npm install --legacy-peer-deps
```

### 1.3 构建 Docker 镜像

```bash
# 构建镜像（替换 yourusername 为你的 Docker Hub 用户名）
docker build -t yourusername/open-webui-custom:latest .

# 或者带版本号
docker build -t yourusername/open-webui-custom:v1.0.0 .
```

---

## Step 2: 推送到镜像仓库

### 方案 A: Docker Hub（公开/私有）

```bash
# 登录 Docker Hub
docker login

# 推送镜像
docker push yourusername/open-webui-custom:latest
```

### 方案 B: GitHub Container Registry (GHCR)

```bash
# 登录 GHCR（需要 GitHub Personal Access Token）
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 标记镜像
docker tag open-webui-custom:latest ghcr.io/yourusername/open-webui-custom:latest

# 推送
docker push ghcr.io/yourusername/open-webui-custom:latest
```

### 方案 C: 阿里云容器镜像服务（国内推荐）

```bash
# 登录阿里云镜像仓库
docker login --username=你的阿里云账号 registry.cn-hangzhou.aliyuncs.com

# 标记镜像
docker tag open-webui-custom:latest registry.cn-hangzhou.aliyuncs.com/你的命名空间/open-webui-custom:latest

# 推送
docker push registry.cn-hangzhou.aliyuncs.com/你的命名空间/open-webui-custom:latest
```

---

## Step 3: 服务器部署

### 3.1 SSH 连接到服务器

```bash
ssh root@your-server-ip
```

### 3.2 安装 Docker（如果没有）

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker
```

### 3.3 拉取并运行

```bash
# 拉取你的自定义镜像
docker pull yourusername/open-webui-custom:latest

# 创建数据目录
mkdir -p /opt/open-webui/data

# 运行容器
docker run -d \
  --name open-webui \
  --restart always \
  -p 3000:8080 \
  -v /opt/open-webui/data:/app/backend/data \
  -e WEBUI_AUTH=true \
  -e ENABLE_SIGNUP=false \
  yourusername/open-webui-custom:latest
```

---

## Step 4: 配置域名和 HTTPS

### 4.1 安装 Nginx

```bash
apt update && apt install -y nginx certbot python3-certbot-nginx
```

### 4.2 配置 Nginx 反向代理

创建 `/etc/nginx/sites-available/open-webui`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超时时间（AI 响应可能较慢）
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 增加上传文件大小限制
    client_max_body_size 100M;
}
```

```bash
# 启用配置
ln -s /etc/nginx/sites-available/open-webui /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 4.3 配置 HTTPS（Let's Encrypt）

```bash
certbot --nginx -d your-domain.com
```

---

## Step 5: 环境变量配置

### 常用环境变量

```bash
docker run -d \
  --name open-webui \
  --restart always \
  -p 3000:8080 \
  -v /opt/open-webui/data:/app/backend/data \
  -e WEBUI_AUTH=true \
  -e ENABLE_SIGNUP=false \
  -e WEBUI_SECRET_KEY="your-secret-key-here" \
  -e OPENAI_API_KEY="sk-xxx" \
  -e ANTHROPIC_API_KEY="sk-ant-xxx" \
  -e DEFAULT_MODELS="gpt-4o,claude-3-opus" \
  yourusername/open-webui-custom:latest
```

---

## 更新部署

当你修改代码后，需要重新构建和部署：

```bash
# 本地
docker build -t yourusername/open-webui-custom:v1.0.1 .
docker push yourusername/open-webui-custom:v1.0.1

# 服务器
docker pull yourusername/open-webui-custom:v1.0.1
docker stop open-webui
docker rm open-webui
docker run -d --name open-webui ... yourusername/open-webui-custom:v1.0.1
```

---

## 一键部署脚本

创建 `deploy.sh`:

```bash
#!/bin/bash
IMAGE_NAME="yourusername/open-webui-custom"
VERSION=${1:-latest}

echo "🚀 Building version: $VERSION"
docker build -t $IMAGE_NAME:$VERSION .

echo "📤 Pushing to registry..."
docker push $IMAGE_NAME:$VERSION

echo "✅ Done! Deploy on server with:"
echo "docker pull $IMAGE_NAME:$VERSION"
```

使用方法：
```bash
./deploy.sh v1.0.0
```

---

## 常见问题

### Q: 构建失败怎么办？
A: 确保使用 Node.js 22，并运行 `npm install --legacy-peer-deps`

### Q: 服务器内存不够？
A: 建议最少 2GB RAM，推荐 4GB+

### Q: 如何备份数据？
A: 备份 `/opt/open-webui/data` 目录

### Q: 如何迁移到新服务器？
A: 1) 备份 data 目录 2) 在新服务器恢复 3) 运行相同的 docker 命令


