# Open WebUI 开发环境设置指南

## ✅ 已完成的设置

1. ✅ Python 3.12 虚拟环境已创建
2. ✅ 后端依赖已安装
3. ✅ 前端依赖已安装
4. ✅ 项目已以开发模式安装

## 🚀 启动开发环境

### 方法 1: 使用一键启动脚本（推荐）

```bash
./dev-start.sh
```

这个脚本会同时启动：
- 前端开发服务器：http://localhost:5173
- 后端 API 服务器：http://localhost:8080

### 方法 2: 分别启动前后端

#### 启动后端（终端 1）

```bash
# 激活虚拟环境
source venv/bin/activate

# 进入后端目录
cd backend

# 启动开发服务器（支持热重载）
bash dev.sh
```

或者直接使用 uvicorn：

```bash
source venv/bin/activate
cd backend
export CORS_ALLOW_ORIGIN="http://localhost:5173;http://localhost:8080"
python -m uvicorn open_webui.main:app --port 8080 --host 0.0.0.0 --forwarded-allow-ips '*' --reload
```

#### 启动前端（终端 2）

```bash
npm run dev
```

前端开发服务器将在 http://localhost:5173 启动

## 📝 开发说明

### 后端开发

- 后端代码位于 `backend/open_webui/` 目录
- 修改 Python 代码后，uvicorn 会自动重载（`--reload` 参数）
- API 文档：http://localhost:8080/docs

### 前端开发

- 前端代码位于 `src/` 目录
- 使用 SvelteKit + TypeScript
- 修改代码后，Vite 会自动热更新
- 支持热模块替换（HMR）

### 常用命令

```bash
# 前端开发
npm run dev              # 启动开发服务器
npm run build            # 构建生产版本
npm run preview          # 预览生产构建
npm run lint:frontend    # 检查前端代码
npm run format           # 格式化代码

# 后端开发
source venv/bin/activate
cd backend
bash dev.sh              # 启动开发服务器
python -m pytest         # 运行测试
black .                  # 格式化 Python 代码
```

## 🔧 环境要求

- Python: 3.12
- Node.js: 18-22 (当前使用 25.2.1，已通过 --engine-strict=false 绕过检查)
- npm: >=6.0.0

## 📚 相关文档

- [Open WebUI 官方文档](https://docs.openwebui.com/)
- [开发指南](https://docs.openwebui.com/getting-started/advanced-topics/development)

## ⚠️ 注意事项

1. **每次开发前**，记得激活虚拟环境：`source venv/bin/activate`
2. **CORS 设置**：开发模式下，后端已配置允许来自 `http://localhost:5173` 的请求
3. **端口占用**：确保 5173 和 8080 端口未被占用
4. **数据库**：开发数据会存储在 `backend/data/` 目录

## 🐛 故障排除

### 前端无法连接后端

检查 `CORS_ALLOW_ORIGIN` 环境变量是否包含前端地址。

### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8080
lsof -i :5173

# 杀死进程
kill -9 <PID>
```

### 依赖问题

```bash
# 重新安装前端依赖
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps --engine-strict=false

# 重新安装后端依赖
source venv/bin/activate
pip install -r backend/requirements.txt
```


