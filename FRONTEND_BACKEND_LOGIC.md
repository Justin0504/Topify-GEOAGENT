# OpenWebUI 前端和后端逻辑说明

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│  浏览器访问: http://localhost:8080                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  后端 (FastAPI + Python)                                 │
│  端口: 8080                                              │
│  进程: uvicorn                                           │
│  代码位置: backend/open_webui/                           │
└─────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌──────────────────┐          ┌──────────────────┐
│  API 端点        │          │  静态文件服务     │
│  /api/v1/*       │          │  /static/*       │
│  /docs           │          │  / (根路径)      │
└──────────────────┘          └──────────────────┘
                                        ↓
                            ┌───────────────────────┐
                            │  build/ 目录          │
                            │  (构建好的前端文件)   │
                            └───────────────────────┘
```

## 📂 代码和文件位置

### 后端代码（Python）
```
backend/open_webui/
├── main.py              # FastAPI 应用入口
├── env.py               # 环境变量和配置（WEBUI_NAME 在这里）
├── config.py            # 配置管理
├── routers/             # API 路由
│   ├── auths.py
│   ├── chats.py
│   ├── models.py
│   └── ...
└── static/              # 静态文件目录
    ├── favicon.png      # Logo 文件（会被服务）
    └── ...
```

**修改后端代码后：**
- ✅ 需要重启后端才能生效
- ✅ 使用 `--reload` 参数可以自动重载（开发模式）

### 前端代码（SvelteKit）
```
src/
├── lib/
│   ├── components/      # 组件
│   ├── stores/         # 状态管理
│   └── constants.ts    # 常量（APP_NAME 在这里）
├── routes/             # 页面路由
└── app.html           # HTML 模板
```

**前端有两种运行模式：**

#### 模式 1: 开发模式（未运行）
```bash
npm run dev
# 运行在: http://localhost:5173
# 特点: 热重载，修改代码立即生效
```

#### 模式 2: 构建模式（当前使用）
```bash
npm run build
# 输出到: build/ 目录
# 特点: 静态文件，由后端服务
```

### 构建后的静态文件
```
build/
├── index.html          # 主页面
├── static/             # 静态资源
│   ├── favicon.png     # Logo（需要同步更新）
│   └── ...
└── _app/               # SvelteKit 应用代码
```

## 🔄 当前运行状态

### 后端
- ✅ **运行中**: uvicorn 在 8080 端口
- 📍 **代码位置**: `backend/open_webui/`
- 🔄 **修改后**: 需要重启后端（或使用 `--reload` 自动重载）

### 前端
- ❌ **开发服务器未运行**: 没有 `npm run dev`
- ✅ **使用构建文件**: `build/` 目录中的静态文件
- 📍 **源代码位置**: `src/`
- 🔄 **修改后**: 需要 `npm run build` 重新构建

## 📝 修改代码的影响

### 1. 修改后端代码（Python）

**位置**: `backend/open_webui/`

**示例修改**:
```python
# backend/open_webui/env.py
WEBUI_NAME = os.environ.get("WEBUI_NAME", "Open WebUI")
# 我们注释掉了自动添加 "(Open WebUI)" 的逻辑
```

**生效方式**:
- 如果使用 `--reload` 参数：自动重载
- 否则：需要手动重启后端

**验证**:
```bash
curl http://localhost:8080/api/config
# 查看返回的 "name" 字段
```

### 2. 修改前端代码（Svelte/TypeScript）

**位置**: `src/`

**示例修改**:
```typescript
// src/lib/constants.ts
export const APP_NAME = 'GEO.AI';
```

**生效方式**:
- **开发模式**: `npm run dev` → 立即生效（热重载）
- **构建模式**: `npm run build` → 需要重新构建

**当前状态**: 
- ❌ 开发服务器未运行
- ✅ 使用构建好的文件（`build/`）
- ⚠️ 修改 `src/` 中的代码**不会立即生效**，需要重新构建

### 3. 修改静态文件（Logo、图片等）

**位置**:
- `backend/open_webui/static/favicon.png` - 后端服务
- `build/static/favicon.png` - 构建后的文件

**生效方式**:
- ✅ 直接替换文件即可
- ⚠️ 可能需要清除浏览器缓存

**我们做的修改**:
```bash
# 替换 Logo
cp "你的Logo.png" backend/open_webui/static/favicon.png
cp "你的Logo.png" build/static/favicon.png
```

## 🎯 访问 localhost:8080 时的流程

```
1. 浏览器请求: http://localhost:8080/
   ↓
2. 后端 FastAPI 接收请求
   ↓
3. 检查路由:
   - 如果是 /api/* → 返回 API 响应
   - 如果是 /static/* → 返回静态文件
   - 如果是 / → 返回 build/index.html
   ↓
4. 浏览器加载 index.html
   ↓
5. index.html 加载 build/_app/ 中的 JS/CSS
   ↓
6. 前端应用启动，调用后端 API
   ↓
7. 显示界面
```

## 📋 我们已做的修改总结

### ✅ 已生效的修改

1. **后端配置** (`backend/open_webui/env.py`)
   - 去掉自动添加 "(Open WebUI)" 的逻辑
   - ✅ 已生效（已重启后端）

2. **Logo 文件**
   - 替换了 `backend/open_webui/static/favicon.png`
   - 替换了 `build/static/favicon.png`
   - ✅ 已生效（清除浏览器缓存后可见）

3. **环境变量**
   - 设置 `WEBUI_NAME='GEO.AI'`
   - ✅ 已生效（后端重启时加载）

### ⚠️ 未生效的修改（需要重新构建）

1. **前端常量** (`src/lib/constants.ts`)
   - `APP_NAME = 'GEO.AI'`
   - ⚠️ 已修改，但需要 `npm run build` 才能生效

2. **前端组件** (`src/lib/components/layout/Sidebar.svelte`)
   - Logo 加载路径的修改
   - ⚠️ 已修改，但需要 `npm run build` 才能生效

## 🔧 如何让前端代码修改生效

### 选项 1: 重新构建（推荐用于生产）
```bash
cd /Users/justin/Downloads/open-webui-main
npm run build
# 这会重新生成 build/ 目录
```

### 选项 2: 启动开发服务器（推荐用于开发）
```bash
cd /Users/justin/Downloads/open-webui-main
npm run dev
# 这会启动开发服务器在 5173 端口
# 然后访问 http://localhost:5173
# 修改代码会立即生效
```

## 📍 关键文件位置速查

| 类型 | 位置 | 修改后需要 |
|------|------|-----------|
| 后端代码 | `backend/open_webui/` | 重启后端 |
| 前端代码 | `src/` | 重新构建或启动开发服务器 |
| Logo 文件 | `backend/open_webui/static/favicon.png` | 清除浏览器缓存 |
| 构建文件 | `build/` | 直接生效（但会被重新构建覆盖） |
| 环境变量 | 启动命令中设置 | 重启后端 |

## 💡 最佳实践

1. **开发时**:
   - 启动前端开发服务器: `npm run dev`
   - 修改代码立即生效
   - 访问 http://localhost:5173

2. **生产/测试时**:
   - 构建前端: `npm run build`
   - 启动后端: `uvicorn ...`
   - 访问 http://localhost:8080

3. **修改 Logo**:
   - 同时替换两个位置
   - 清除浏览器缓存

4. **修改配置**:
   - 后端配置 → 重启后端
   - 前端配置 → 重新构建

