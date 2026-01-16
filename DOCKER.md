# Docker 部署指南

本文档说明如何使用 Docker 和 Docker Compose 部署表格提取工具。

## ? 前置要求

- Docker（版本 20.10+）
- Docker Compose（版本 2.0+）

## ? 快速开始

### 1. 准备环境变量文件

在项目根目录创建 `.env` 文件（如果不存在）：

```bash
# 复制示例文件
cp env.example .env
```

### 2. 配置环境变量

编辑 `.env` 文件，根据你的部署环境修改配置：

#### 本地部署（默认）

```env
DEPLOY_MODE=local
PORT=5000
FRONTEND_PORT=80
```

#### 云部署（使用公网IP）

```env
DEPLOY_MODE=cloud
PUBLIC_IP=123.45.67.89
PORT=5000
FRONTEND_PORT=80
```

#### 云部署（使用域名）

```env
DEPLOY_MODE=cloud
PUBLIC_DOMAIN=your-domain.com
PORT=5000
FRONTEND_PORT=80
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问应用

- **前端**: http://localhost:80（或你配置的 `FRONTEND_PORT`）
- **后端 API**: http://localhost:5000（或你配置的 `PORT`）

## ? 数据持久化

以下数据会自动持久化到宿主机：

- **数据库**: `./backend/instance/table_extractor.db`
- **上传文件**: `./backend/uploads/`
- **环境变量**: `./.env`

**重要**: 这些目录和文件会在容器重启后保留，确保数据不丢失。

## ? 常用命令

### 启动服务

```bash
docker-compose up -d
```

### 停止服务

```bash
docker-compose stop
```

### 停止并删除容器

```bash
docker-compose down
```

### 停止并删除容器、网络、卷（**注意：会删除数据卷**）

```bash
docker-compose down -v
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend
```

### 重新构建镜像

```bash
# 重新构建所有镜像
docker-compose build

# 重新构建特定服务
docker-compose build backend
docker-compose build frontend

# 强制重新构建（不使用缓存）
docker-compose build --no-cache
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend sh

# 进入前端容器
docker-compose exec frontend sh
```

## ? 健康检查

服务包含健康检查功能：

- **后端**: `http://localhost:5000/api/health`
- **前端**: `http://localhost/`

查看健康状态：

```bash
docker-compose ps
```

## ?? 故障排查

### 1. 端口被占用

如果端口被占用，修改 `.env` 文件中的端口配置：

```env
PORT=5001
FRONTEND_PORT=8080
```

然后重启服务：

```bash
docker-compose down
docker-compose up -d
```

### 2. 数据库初始化

如果数据库不存在，容器启动时会自动创建。你也可以手动初始化：

```bash
docker-compose exec backend python init_db.py
```

### 3. 查看详细日志

```bash
# 查看后端日志
docker-compose logs backend

# 查看前端日志
docker-compose logs frontend

# 实时查看所有日志
docker-compose logs -f
```

### 4. 重置环境

如果需要完全重置（**注意：会删除所有数据**）：

```bash
# 停止并删除容器、网络、卷
docker-compose down -v

# 删除镜像
docker-compose rm -f

# 重新构建并启动
docker-compose up -d --build
```

## ? 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `DEPLOY_MODE` | 部署模式：`local` 或 `cloud` | `local` | 否 |
| `PUBLIC_IP` | 公网IP（云部署时使用） | - | 否 |
| `PUBLIC_DOMAIN` | 域名（云部署时使用） | - | 否 |
| `PORT` | 后端服务端口 | `5000` | 否 |
| `FRONTEND_PORT` | 前端服务端口 | `80` | 否 |
| `SECRET_KEY` | Flask 密钥 | `dev-secret-key-change-in-production` | 否 |
| `DATABASE_URL` | 数据库连接URL | `sqlite:///table_extractor.db` | 否 |
| `UPLOAD_FOLDER` | 上传文件目录 | `uploads` | 否 |
| `MAX_FILE_SIZE` | 最大文件大小（字节） | `10485760` | 否 |
| `CORS_ORIGINS` | CORS允许的源（逗号分隔） | 自动生成 | 否 |
| `VITE_API_URL` | 前端API地址（生产环境） | 自动生成 | 否 |

## ? 安全建议

1. **生产环境**：修改 `SECRET_KEY` 为强随机字符串
2. **HTTPS**：在生产环境使用 HTTPS（需要配置反向代理，如 Nginx）
3. **防火墙**：只开放必要的端口
4. **定期备份**：定期备份 `./backend/instance/` 和 `./backend/uploads/` 目录

## ? 更多信息

- 查看 [README.md](README.md) 了解项目详情
- 查看 [DEPLOY.md](DEPLOY.md) 了解部署配置
- 查看 [INSTALL.md](INSTALL.md) 了解安装步骤

