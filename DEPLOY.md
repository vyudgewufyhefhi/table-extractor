# 云部署指南

## 概述

本项目支持通过环境变量灵活配置部署地址，适用于本地开发、云服务器部署等场景。

**重要**：所有环境变量统一在**根目录的 `.env` 文件**中配置，无需在子目录创建单独的.env文件。

## 配置说明

### 1. 根目录环境变量配置

在项目根目录创建 `.env` 文件（可参考根目录的 `.env` 文件）：

```env
# Flask应用配置
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///table_extractor.db
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760

# 服务器配置
HOST=0.0.0.0  # 监听所有网络接口
PORT=5000

# CORS配置（允许的前端地址，多个地址用逗号分隔）
# 云部署示例（使用公网IP）：
# CORS_ORIGINS=http://your-public-ip:5173,http://your-public-ip:3000
# 云部署示例（使用域名）：
# CORS_ORIGINS=http://your-domain.com,https://your-domain.com
# 如果不确定域名，可以使用通配符（不推荐生产环境）：
# CORS_ORIGINS=*
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 2. 前端配置 (frontend/.env)

创建 `frontend/.env` 文件（可参考 `frontend/.env.example`）：

#### 开发环境
```env
# 使用相对路径，由vite代理处理
VITE_API_URL=
VITE_PORT=5173
```

#### 生产环境
```env
# 配置完整的后端API地址
VITE_API_URL=http://your-public-ip:5000/api
# 或使用域名
# VITE_API_URL=https://your-domain.com/api
```

## 部署步骤

### 方案一：前后端分离部署

#### 1. 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（编辑 .env 文件）
# 设置 CORS_ORIGINS 为你的前端地址

# 5. 初始化数据库
python init_db.py

# 6. 启动服务
python app.py
# 或使用 gunicorn（推荐生产环境）
# gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 2. 前端部署

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 配置环境变量（编辑根目录的 .env 文件）
# 设置 DEPLOY_MODE=cloud 和 PUBLIC_IP 或 PUBLIC_DOMAIN
# VITE_API_URL 会根据这些配置自动生成

# 4. 构建生产版本
npm run build

# 5. 部署 dist 目录到静态文件服务器
# 可以使用 nginx、apache 等
```

### 方案二：使用 Nginx 反向代理（推荐）

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 或使用公网IP

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

使用 Nginx 时：
- 后端 `.env` 中的 `CORS_ORIGINS` 设置为前端域名（如：`http://your-domain.com`）
- 前端 `.env` 中的 `VITE_API_URL` 留空（使用相对路径 `/api`）

### 方案三：前后端同域名部署

如果前后端使用同一个域名和端口：

1. **后端配置**：`CORS_ORIGINS` 设置为该域名
2. **前端配置**：`VITE_API_URL` 设置为 `/api`（相对路径）

## 防火墙配置

确保服务器防火墙开放以下端口：
- 后端端口（默认 5000）
- 前端端口（开发环境默认 5173，生产环境由 Web 服务器配置）

## 常见问题

### 1. CORS 错误

**问题**：浏览器控制台显示 CORS 错误

**解决**：
- 检查后端 `.env` 中的 `CORS_ORIGINS` 是否包含前端地址
- 确保前后端协议一致（http 或 https）
- 确保端口号正确

### 2. API 请求失败

**问题**：前端无法连接到后端 API

**解决**：
- 检查后端服务是否正常运行
- 检查根目录 `.env` 中的 `DEPLOY_MODE`、`PUBLIC_IP` 或 `PUBLIC_DOMAIN` 配置
- 检查 `VITE_API_URL` 是否正确生成（可在浏览器控制台查看）
- 检查防火墙设置
- 检查网络连接

### 3. 文件上传失败

**问题**：上传文件时出错

**解决**：
- 检查 `UPLOAD_FOLDER` 目录权限
- 检查 `MAX_FILE_SIZE` 配置是否足够

## 环境变量参考

### 后端环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `SECRET_KEY` | Flask密钥 | `dev-secret-key` | `your-secret-key` |
| `DATABASE_URL` | 数据库URL | `sqlite:///table_extractor.db` | `sqlite:///table_extractor.db` |
| `UPLOAD_FOLDER` | 上传文件夹 | `uploads` | `uploads` |
| `MAX_FILE_SIZE` | 最大文件大小（字节） | `10485760` | `10485760` |
| `HOST` | 监听地址 | `0.0.0.0` | `0.0.0.0` |
| `PORT` | 监听端口 | `5000` | `5000` |
| `CORS_ORIGINS` | 允许的源（可选，自动生成） | 自动根据部署模式生成 | `http://your-domain.com` |
| `DEPLOY_MODE` | 部署模式 | `local` | `cloud` |
| `PUBLIC_IP` | 公网IP（云部署） | - | `123.45.67.89` |
| `PUBLIC_DOMAIN` | 域名（云部署，优先使用） | - | `your-domain.com` |

### 前端环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `VITE_API_URL` | API地址（可选，自动生成） | 自动根据部署模式生成 | `http://your-ip:5000/api` |
| `VITE_PORT` | 开发服务器端口 | `5173` | `5173` |

## 安全建议

1. **生产环境**：
   - 使用 HTTPS
   - 设置强密码的 `SECRET_KEY`
   - 限制 `CORS_ORIGINS` 为特定域名，不要使用通配符
   - 使用专业 Web 服务器（如 Nginx）而不是直接暴露 Flask 服务

2. **文件安全**：
   - 限制文件上传大小
   - 验证文件类型
   - 定期清理临时文件

3. **数据库安全**：
   - 使用数据库密码
   - 定期备份数据

