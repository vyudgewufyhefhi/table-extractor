# 表格提取工具

基于**AI + 手动文本**的智能表格提取系统，无需上传文件，只需复制提示词给AI，粘贴结果即可生成Excel。

## 功能特性

- [√] 用户注册登录系统
- [√] 一键复制提示词给AI
- [√] 纯文本解析为表格结构
- [√] 自动生成Excel文件（无背景色、黑色文字、居中、单行显示）
- [√] 完整的历史记录管理（全选、批量删除、查看文本、下载Excel）
- [√] 自动清理孤立文件（无需手动操作）
- [√] Excel文件下载
- [√] 数据持久化（数据库、文件、环境变量）

## 技术栈

- **前端**：Vue 3 + Element Plus + Vite
- **后端**：Flask + SQLAlchemy
- **数据库**：SQLite
- **Python版本**：3.11
- **部署**：Docker + Docker Compose

## 安装步骤

### 方式一：本地开发

#### 1. 创建虚拟环境

```bash
python -m venv .venv
```

#### 2. 激活虚拟环境

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

#### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
DEPLOY_MODE=local
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///table_extractor.db
UPLOAD_FOLDER=uploads
PORT=5000
VITE_PORT=5173
```

#### 5. 初始化数据库

```bash
python init_db.py
```

#### 6. 启动后端服务

```bash
python app.py
```

后端将在 `http://localhost:5000` 运行

#### 7. 安装前端依赖

打开**新的终端窗口**：

```bash
cd frontend
npm install
```

#### 8. 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 运行

### 方式二：Docker 部署（推荐）

#### 1. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# 部署模式
DEPLOY_MODE=local  # 或 cloud（云部署）

# 后端配置
SECRET_KEY=your-secret-key-change-in-production
PORT=5000

# 前端配置
FRONTEND_PORT=80

# 云部署配置（如果 DEPLOY_MODE=cloud）
# PUBLIC_IP=your-public-ip
# PUBLIC_DOMAIN=your-domain.com
```

#### 2. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 3. 访问应用

- **前端**: http://localhost:80
- **后端 API**: http://localhost:5000

## 使用流程

### 第一步：注册/登录

1. 访问应用地址（本地：`http://localhost:5173`，Docker：`http://localhost:80`）
2. 注册账号（用户名唯一，密码至少6位）
3. 登录进入主页面

### 第二步：复制提示词给AI

1. 在主页面的"步骤一"区域，点击"**复制提示词**"
2. 打开AI工具（如豆包、ChatGPT、Claude等），粘贴提示词
3. 上传你的PDF文件给AI
4. 等待AI处理并返回纯文本结果

### 第三步：粘贴结果并生成Excel

1. 将AI返回的纯文本**完整复制**
2. 粘贴到主页面的"步骤二"大文本框中
3. 确保格式正确（每行一条记录，列之间用空格分隔）
4. 点击"**生成Excel**"按钮
5. 预览表格，确认无误后点击"**下载Excel**"
6. 如需保存，点击"**存入历史记录**"按钮

### 第四步：查看历史记录

- 点击顶部"历史记录"查看所有生成记录
- 支持全选、批量删除、查看原始文本、下载Excel
- 所有操作都会自动清理对应的Excel文件

## 项目结构

```
表格提取工具/
├── backend/              # 后端代码
│   ├── app.py           # Flask主应用
│   ├── models.py        # 数据模型（User, FileRecord, TextRecord）
│   ├── auth.py          # 用户认证
│   ├── excel_utils.py   # Excel生成工具
│   ├── init_db.py       # 数据库初始化
│   ├── requirements.txt # Python依赖
│   └── Dockerfile       # 后端Docker镜像
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   │   ├── Home.vue      # 主页面
│   │   │   ├── History.vue   # 历史记录
│   │   │   ├── Login.vue     # 登录页
│   │   │   └── Register.vue # 注册页
│   │   ├── api/         # API接口
│   │   ├── router/      # 路由配置
│   │   └── stores/      # 状态管理
│   ├── Dockerfile       # 前端Docker镜像
│   ├── nginx.conf       # Nginx配置
│   └── vite.config.js   # Vite配置
├── instance/            # 数据库存储目录（根目录）
│   └── table_extractor.db
├── uploads/             # 文件存储目录（根目录）
│   └── excel/           # Excel文件存储
├── docker-compose.yml   # Docker Compose配置
├── .env                 # 环境变量配置（需要创建）
├── env.example          # 环境变量示例
└── README.md            # 项目说明
```

## 使用技巧

1. **分屏操作**：左屏打开本工具，右屏打开PDF阅读器和AI工具，方便对照
2. **文本格式**：确保AI返回的文本每行一条记录，列之间用空格分隔
3. **历史记录**：所有生成记录都会保存，可以随时查看和下载
4. **批量操作**：历史记录支持全选和批量删除，提高效率
5. **自动清理**：系统会自动清理未保存的临时文件，无需手动操作

## 环境变量配置

项目使用统一的 `.env` 文件进行配置，支持本地开发和云部署：

### 本地开发配置

```env
# 部署模式
DEPLOY_MODE=local

# 后端配置
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///table_extractor.db  # 数据库会自动创建在根目录的 instance/ 目录
UPLOAD_FOLDER=uploads  # 上传文件存储在根目录的 uploads/
PORT=5000

# 前端配置
VITE_PORT=5173
```

### 云部署配置

```env
# 部署模式
DEPLOY_MODE=cloud

# 公网IP/域名配置
PUBLIC_IP=123.45.67.89  # 或使用域名
PUBLIC_DOMAIN=your-domain.com

# 后端配置
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///table_extractor.db  # 数据库存储在根目录的 instance/ 目录
UPLOAD_FOLDER=uploads  # 上传文件存储在根目录的 uploads/
PORT=5000

# 前端配置
FRONTEND_PORT=80
VITE_API_URL=http://123.45.67.89/api  # 或使用域名
```

### 路径说明

- **数据库路径**：统一存储在根目录的 `instance/table_extractor.db`
- **上传文件路径**：统一存储在根目录的 `uploads/` 目录
- **Excel文件路径**：存储在 `uploads/excel/` 目录

详细配置说明请参考 `env.example` 文件。

## Docker 部署

### 快速开始

1. 配置 `.env` 文件
2. 运行 `docker-compose up -d`
3. 访问 http://localhost:80

### 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 重新构建
docker-compose build --no-cache
```

### 数据持久化

以下数据会自动持久化到宿主机：

- **数据库**: `./instance/table_extractor.db`（根目录）
- **上传文件**: `./uploads/`（根目录）
- **环境变量**: `./.env`

## 注意事项

- [√] **不需要上传文件**：所有文件处理都在AI工具中完成
- [√] **文本格式很重要**：确保AI返回的格式符合要求（每行一条记录，列之间用空格分隔）
- [√] **历史记录会保存**：所有生成的记录都会保存到数据库
- [√] **自动清理机制**：系统会自动清理未保存的临时文件（超过1小时或用户生成新文件时）
- [√] **数据持久化**：数据库、上传文件、环境变量都会持久化保存

## 常见问题

**Q: 后端启动失败？**  
A: 检查Python版本（需要3.11）、虚拟环境、依赖安装、端口占用

**Q: 前端启动失败？**  
A: 检查Node.js版本、依赖安装、端口占用

**Q: Excel生成失败？**  
A: 检查文本格式是否正确，查看后端日志

**Q: Docker部署后无法访问？**  
A: 检查端口映射、防火墙设置、环境变量配置

**Q: 数据库文件在哪里？**  
A: 统一存储在根目录的 `instance/table_extractor.db`

**Q: 如何备份数据？**  
A: 备份根目录的 `instance/` 目录（数据库）和 `uploads/` 目录（Excel文件）

## 安全建议

1. **生产环境**：修改 `SECRET_KEY` 为强随机字符串
2. **HTTPS**：在生产环境使用 HTTPS（需要配置反向代理）
3. **防火墙**：只开放必要的端口
4. **定期备份**：定期备份数据库和上传文件目录

## 更新日志

### 最新版本

- [√] **统一路径配置**：数据库和上传文件统一存储在根目录
  - 数据库：`instance/table_extractor.db`（根目录，不再使用 `backend/instance/`）
  - 上传文件：`uploads/`（根目录，不再使用 `backend/uploads/`）
  - 删除无用的 `temp_images` 目录
- [√] 添加全选/取消全选功能
- [√] 实现自动清理孤立文件机制
- [√] 优化UI：统一提醒颜色、移除新建任务按钮
- [√] 支持Docker部署
- [√] 统一环境变量配置
- [√] 修复编码问题

---

**祝你使用愉快！**
