# 安装说明

## 系统要求

- Python 3.11
- Node.js 16+ 和 npm
- Windows/Linux/MacOS

## 后端安装

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

### 2. 激活虚拟环境

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 安装Poppler（PDF处理需要）

**Windows:**
1. 下载Poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases/
2. 解压到一个目录（如 `C:\poppler`）
3. 将 `bin` 目录添加到系统PATH环境变量
4. 或者设置环境变量：`POPPLER_PATH=C:\poppler\Library\bin`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install poppler-utils
```

**Mac:**
```bash
brew install poppler
```

### 5. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下配置：

```env
# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# 数据库配置
DATABASE_URL=sqlite:///table_extractor.db

# Qwen API配置（重要！）
QWEN_API_KEY=your-qwen-api-key-here
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-vl-max

# 文件上传配置
UPLOAD_FOLDER=backend/uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,png,jpg,jpeg

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

**重要：** 需要从阿里云获取Qwen API密钥：
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录账号
3. 创建API Key
4. 将API Key填入 `.env` 文件的 `QWEN_API_KEY`

### 6. 初始化数据库

```bash
python init_db.py
```

### 7. 启动后端服务

```bash
python app.py
```

或者使用启动脚本（Windows）：
```bash
start.bat
```

后端将在 http://localhost:5000 运行

## 前端安装

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

或者使用启动脚本（Windows）：
```bash
start.bat
```

前端将在 http://localhost:5173 运行

## 使用说明

1. 打开浏览器访问 http://localhost:5173
2. 注册一个新账号（用户名至少3个字符，密码至少6个字符）
3. 登录后，可以上传PDF或图片文件
4. 点击"开始识别"进行AI识别
5. 查看识别结果，可以编辑校正数据
6. 点击"生成Excel"生成Excel文件
7. 可以下载或复制Excel文件链接

## 常见问题

### 1. PDF转换失败

**问题：** 提示 "PDF转换失败" 或 "poppler not found"

**解决：**
- 确保已安装Poppler
- Windows用户需要将Poppler的bin目录添加到PATH
- 或者设置环境变量 `POPPLER_PATH`

### 2. Qwen API调用失败

**问题：** 提示 "API调用失败" 或 "API密钥未配置"

**解决：**
- 检查 `.env` 文件中的 `QWEN_API_KEY` 是否正确
- 确认API密钥有效且有足够的余额
- 检查网络连接

### 3. 前端无法连接后端

**问题：** 前端显示连接错误

**解决：**
- 确认后端服务正在运行（http://localhost:5000）
- 检查 `frontend/vite.config.js` 中的代理配置
- 检查CORS设置

### 4. 数据库错误

**问题：** 数据库相关错误

**解决：**
- 运行 `python backend/init_db.py` 重新初始化数据库
- 检查数据库文件权限
- 确认SQLite可用

## 生产环境部署

### 后端

1. 修改 `.env` 文件：
   - 设置 `FLASK_ENV=production`
   - 设置 `FLASK_DEBUG=False`
   - 使用强随机密钥作为 `SECRET_KEY`

2. 使用生产级WSGI服务器（如Gunicorn）：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 前端

1. 构建生产版本：
```bash
cd frontend
npm run build
```

2. 部署 `dist` 目录到Web服务器（如Nginx）

3. 配置Nginx反向代理到后端API

## 技术支持

如遇到问题，请检查：
1. 日志文件
2. 浏览器控制台错误
3. 后端终端输出
4. 环境变量配置

