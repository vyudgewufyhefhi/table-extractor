# 表格提取工具

基于**豆包AI + 手动文本**的智能表格提取系统，无需上传文件，只需复制提示词给豆包，粘贴结果即可生成Excel。

## ? 功能特性

- ? 用户注册登录系统
- ? 一键复制提示词给豆包
- ? 纯文本解析为表格结构
- ? 自动生成Excel文件
- ? 完整的历史记录管理
- ? Excel文件下载

## ?? 技术栈

- **前端**：Vue 3 + Element Plus + Vite
- **后端**：Flask + SQLAlchemy
- **数据库**：SQLite
- **Python版本**：3.11

## ? 安装步骤

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

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动后端服务

```bash
python app.py
```

后端将在 `http://localhost:5000` 运行

### 6. 安装前端依赖

打开**新的终端窗口**：

```bash
cd frontend
npm install
```

### 7. 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 运行

## ? 使用流程

### 第一步：注册/登录

1. 访问 `http://localhost:5173`
2. 注册账号（用户名唯一，密码至少6位）
3. 登录进入主页面

### 第二步：复制提示词给豆包

1. 在主页面的"步骤一"区域，点击"**复制提示词**"
2. 打开豆包（网页版或APP），粘贴提示词
3. 上传你的PDF文件给豆包
4. 等待豆包处理并返回纯文本结果

### 第三步：粘贴结果并生成Excel

1. 将豆包返回的纯文本**完整复制**
2. 粘贴到主页面的"步骤二"大文本框中
3. 确保格式正确（每行一条记录，列之间用空格分隔）
4. 点击"**生成Excel**"按钮
5. 下载生成的Excel文件

### 第四步：查看历史记录

- 点击顶部"历史记录"查看所有生成记录
- 可以查看原始文本和下载Excel

## ? 项目结构

```
表格提取工具/
├── backend/              # 后端代码
│   ├── app.py           # Flask主应用
│   ├── models.py        # 数据模型（User, FileRecord, TextRecord）
│   ├── auth.py          # 用户认证
│   ├── excel_utils.py   # Excel生成工具
│   ├── init_db.py       # 数据库初始化
│   └── requirements.txt # Python依赖
├── frontend/            # 前端代码
│   └── src/
│       └── views/
│           ├── Home.vue      # 主页面（提示词+文本输入）
│           ├── History.vue   # 历史记录
│           ├── Login.vue     # 登录页
│           └── Register.vue # 注册页
├── uploads/             # 文件存储
│   └── excel/           # Excel文件存储
└── 使用指南.md          # 详细使用说明
```

## ? 使用技巧

1. **分屏操作**：左屏打开本工具，右屏打开PDF阅读器和豆包，方便对照
2. **文本格式**：确保豆包返回的文本每行一条记录，列之间用空格分隔
3. **历史记录**：所有生成记录都会保存，可以随时查看和下载

## ? 注意事项

- ? **不需要上传文件**：所有文件处理都在豆包中完成
- ? **文本格式很重要**：确保豆包返回的格式符合要求
- ? **历史记录会保存**：所有生成的记录都会保存

## ? 常见问题

**Q: 后端启动失败？**  
A: 检查Python版本、虚拟环境、依赖安装

**Q: 前端启动失败？**  
A: 检查Node.js版本、依赖安装、端口占用

**Q: Excel生成失败？**  
A: 检查文本格式是否正确，查看后端日志

## ? 详细文档

更多使用说明请查看 [使用指南.md](./使用指南.md)

---

**祝你使用愉快！** ?
