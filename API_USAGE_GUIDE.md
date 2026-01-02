# OpenWebUI API 使用指南

## 🔌 当前 API 状态

你的 OpenWebUI 后端正在运行，提供完整的 REST API。

### 基础信息
- **API 基础 URL**: `http://localhost:8080`
- **API 版本**: `/api/v1`
- **API 文档**: `http://localhost:8080/docs` (Swagger UI)
- **状态**: ✅ 运行中

## 📡 主要 API 端点

### 1. 配置信息
```bash
GET /api/config
```
无需认证，返回应用配置信息。

### 2. 认证相关
```bash
POST /api/v1/auths/signup       # 注册
POST /api/v1/auths/signin       # 登录
GET  /api/v1/auths/session      # 获取会话信息
```

### 3. 聊天相关
```bash
GET    /api/v1/chats            # 获取聊天列表
POST   /api/v1/chats            # 创建新聊天
GET    /api/v1/chats/{id}       # 获取特定聊天
PUT    /api/v1/chats/{id}       # 更新聊天
DELETE /api/v1/chats/{id}       # 删除聊天
```

### 4. 模型相关
```bash
GET /api/v1/models              # 获取模型列表
```

### 5. 消息相关
```bash
POST /api/v1/chats/{id}/messages  # 发送消息
GET  /api/v1/chats/{id}/messages  # 获取消息列表
```

## 🔐 认证方式

### 方式 1: Bearer Token（推荐）

```bash
# 1. 先登录获取 token
curl -X POST http://localhost:8080/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "your_password"
  }'

# 返回的响应中包含 token
# {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "user": {...}
# }

# 2. 使用 token 访问 API
curl http://localhost:8080/api/v1/chats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 方式 2: API Key（如果启用）

```bash
curl http://localhost:8080/api/v1/chats \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 💻 使用示例

### Python 示例

```python
import requests

# API 基础 URL
BASE_URL = "http://localhost:8080"

# 1. 登录获取 token
def login(email, password):
    response = requests.post(
        f"{BASE_URL}/api/v1/auths/signin",
        json={"email": email, "password": password}
    )
    return response.json()["token"]

# 2. 获取聊天列表
def get_chats(token):
    response = requests.get(
        f"{BASE_URL}/api/v1/chats",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

# 3. 创建新聊天
def create_chat(token, title="New Chat"):
    response = requests.post(
        f"{BASE_URL}/api/v1/chats",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": title}
    )
    return response.json()

# 使用
token = login("your@email.com", "password")
chats = get_chats(token)
print(chats)
```

### JavaScript/TypeScript 示例

```javascript
const BASE_URL = "http://localhost:8080";

// 登录
async function login(email, password) {
  const response = await fetch(`${BASE_URL}/api/v1/auths/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  return data.token;
}

// 获取聊天列表
async function getChats(token) {
  const response = await fetch(`${BASE_URL}/api/v1/chats`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  return await response.json();
}

// 使用
const token = await login("your@email.com", "password");
const chats = await getChats(token);
console.log(chats);
```

### cURL 示例

```bash
# 获取配置（无需认证）
curl http://localhost:8080/api/config

# 登录
curl -X POST http://localhost:8080/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"password"}'

# 获取聊天列表（需要 token）
curl http://localhost:8080/api/v1/chats \
  -H "Authorization: Bearer YOUR_TOKEN"

# 创建聊天
curl -X POST http://localhost:8080/api/v1/chats \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My New Chat"}'
```

## 🔍 查看完整 API 文档

访问 Swagger UI 查看所有可用的 API 端点：

```
http://localhost:8080/docs
```

在 Swagger UI 中，你可以：
- 查看所有 API 端点
- 查看请求/响应格式
- 直接在浏览器中测试 API
- 查看认证要求

## 🔗 在你的应用中使用

### 从外部应用连接

如果你有其他应用需要连接到 OpenWebUI API：

1. **本地连接**:
   ```python
   BASE_URL = "http://localhost:8080"
   ```

2. **远程连接**:
   ```python
   BASE_URL = "https://your-domain.com"  # 你的 OpenWebUI 服务器地址
   ```

3. **处理 CORS**（如果需要跨域）:
   - 设置环境变量: `CORS_ALLOW_ORIGIN=your-frontend-url`
   - 或修改后端配置

### 从前端页面连接

```javascript
// 在同一域名下，可以直接使用相对路径
const response = await fetch("/api/v1/chats", {
  headers: {
    "Authorization": `Bearer ${localStorage.token}`
  }
});
```

## 🔧 配置 API 访问

### 启用 API Key（可选）

1. 在管理员设置中启用 API Key
2. 生成 API Key
3. 使用 API Key 进行认证

### 环境变量

```bash
# 启用 API Key
ENABLE_API_KEYS=true

# CORS 设置（如果需要跨域访问）
CORS_ALLOW_ORIGIN=http://localhost:3000,https://your-app.com
```

## 📊 当前 API 状态

运行以下命令检查 API 状态：

```bash
# 检查 API 是否运行
curl http://localhost:8080/health

# 获取配置信息
curl http://localhost:8080/api/config

# 查看 API 文档
open http://localhost:8080/docs
```

## 💡 常见用例

### 1. 集成到你的工具中

你的 `article_writer_tool.py` 可以调用 OpenWebUI API：

```python
import requests

def call_openwebui_api(prompt, model="gpt-4"):
    response = requests.post(
        "http://localhost:8080/api/v1/chats/completions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "messages": [{"role": "user", "content": prompt}],
            "model": model
        }
    )
    return response.json()
```

### 2. 批量处理

```python
def batch_create_chats(topics, token):
    chats = []
    for topic in topics:
        chat = requests.post(
            "http://localhost:8080/api/v1/chats",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": topic}
        ).json()
        chats.append(chat)
    return chats
```

## 🚀 下一步

1. **查看 API 文档**: 访问 http://localhost:8080/docs
2. **测试 API**: 使用 Swagger UI 或 cURL 测试
3. **集成到你的应用**: 使用上面的示例代码

