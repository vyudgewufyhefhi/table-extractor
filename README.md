# 表格提取工具

基于Qwen视觉模型的智能表格提取系统，支持PDF和图片的表格识别与编辑。

## 功能特性

- 用户注册登录系统
- 支持PDF和图片文件上传（拖拽、复制、批量上传）
- 高清文件预览
- AI智能表格识别（Qwen视觉模型）
- 实时识别结果展示
- 表格数据编辑校正
- Excel文件生成和下载
- 完整的历史记录功能

## 技术栈

- 前端：Vue 3 + Element Plus
- 后端：Flask + SQLAlchemy
- AI模型：Qwen视觉模型
- 数据库：SQLite
- Python版本：3.11

## 安装步骤

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

### 2. 激活虚拟环境

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入Qwen API密钥等信息。

### 5. 初始化数据库

```bash
python init_db.py
```

### 6. 启动后端服务

```bash
python app.py
```

后端将在 http://localhost:5000 运行

### 7. 安装前端依赖

```bash
cd frontend
npm install
```

### 8. 启动前端开发服务器

```bash
npm run dev
```

前端将在 http://localhost:5173 运行

## 项目结构

```
表格提取工具/
├── backend/              # 后端代码
│   ├── app.py           # Flask主应用
│   ├── models.py        # 数据库模型
│   ├── auth.py          # 认证相关
│   ├── ai_service.py    # AI模型调用
│   ├── file_utils.py    # 文件处理工具
│   ├── requirements.txt # Python依赖
│   └── uploads/         # 上传文件存储
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── components/  # 通用组件
│   │   ├── api/         # API调用
│   │   └── router/      # 路由配置
│   └── package.json
├── .env                 # 环境变量配置
└── README.md
```

## 使用说明

1. 注册账号并登录
2. 上传包含表格的PDF或图片文件
3. 点击"开始识别"进行AI识别
4. 查看识别结果并与原文件比对
5. 编辑校正识别错误的数据
6. 点击"生成表格"生成Excel文件
7. 下载或复制Excel文件

