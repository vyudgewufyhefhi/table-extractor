# 快速启动指南

## 1. 后端启动（5分钟）

### Windows用户

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
.venv\Scripts\activate

# 3. 安装依赖
cd backend
pip install -r requirements.txt

# 4. 配置环境变量
# 复制项目根目录的 .env.example 为 .env
# 编辑 .env，填入你的 QWEN_API_KEY

# 5. 初始化数据库
python init_db.py

# 6. 启动服务
python app.py
```

### Linux/Mac用户

```bash
# 1. 创建虚拟环境
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
cd backend
pip install -r requirements.txt

# 4. 安装Poppler（PDF处理需要）
# Ubuntu/Debian:
sudo apt-get install poppler-utils
# Mac:
brew install poppler

# 5. 配置环境变量
# 复制项目根目录的 .env.example 为 .env
# 编辑 .env，填入你的 QWEN_API_KEY

# 6. 初始化数据库
python init_db.py

# 7. 启动服务
python app.py
```

## 2. 前端启动（2分钟）

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

## 3. 访问应用

打开浏览器访问：http://localhost:5173

## 4. 获取Qwen API密钥

1. 访问：https://dashscope.console.aliyun.com/
2. 注册/登录账号
3. 进入"API-KEY管理"
4. 创建新的API Key
5. 将API Key复制到 `.env` 文件的 `QWEN_API_KEY` 字段

## 5. 使用流程

1. **注册账号**：用户名至少3个字符，密码至少6个字符
2. **上传文件**：支持PDF、PNG、JPG格式，可批量上传
3. **开始识别**：点击"开始识别"按钮，AI会逐个识别文件
4. **编辑数据**：查看识别结果，可以编辑校正表格数据
5. **生成Excel**：点击"生成Excel"按钮生成Excel文件
6. **下载文件**：可以下载或复制Excel文件链接

## 常见问题快速解决

### PDF转换失败
- **Windows**: 下载Poppler，解压后设置环境变量 `POPPLER_PATH`
- **Linux**: `sudo apt-get install poppler-utils`
- **Mac**: `brew install poppler`

### API调用失败
- 检查 `.env` 文件中的 `QWEN_API_KEY` 是否正确
- 确认API密钥有效且有余额

### 前端无法连接后端
- 确认后端正在运行（http://localhost:5000）
- 检查浏览器控制台错误信息

