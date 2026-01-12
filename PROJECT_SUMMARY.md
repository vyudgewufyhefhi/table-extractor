# 项目功能总结

## 已实现功能

### 1. 用户系统 ?
- **注册功能**：用户名唯一性验证，至少3个字符，只能包含字母、数字和下划线
- **登录功能**：密码验证，至少6个字符
- **用户数据**：存储在SQLite数据库中，使用bcrypt加密密码
- **会话管理**：前端使用localStorage存储用户信息

### 2. 文件上传 ?
- **支持格式**：PDF、PNG、JPG、JPEG
- **上传方式**：
  - 拖拽上传
  - 点击上传
  - 批量上传（可同时选择多个文件）
- **文件处理**：
  - 自动生成唯一文件名
  - 文件大小限制：10MB
  - 文件类型验证

### 3. 文件预览 ?
- **高清预览**：支持PDF和图片的高清预览
- **批量预览**：批量上传时，可以选择预览哪个文件
- **预览功能**：
  - PDF预览（转换为图片）
  - 图片预览（直接显示）
  - 全屏预览功能

### 4. AI表格识别 ?
- **模型集成**：集成Qwen视觉模型（qwen-vl-max）
- **识别功能**：
  - 支持PDF多页识别
  - 支持图片识别
  - 自动处理跨页表格
  - 自动合并多行显示的数据
- **实时显示**：每个文件识别完成后立即显示结果，不需要等待所有文件完成
- **识别结果**：返回结构化的表格数据（headers和rows）

### 5. 表格编辑 ?
- **数据编辑**：用户可以编辑识别出的表格数据
- **实时保存**：编辑后自动保存到数据库
- **数据对比**：左侧编辑，右侧预览原文件，方便对比
- **多页支持**：支持多页PDF的表格编辑

### 6. Excel生成 ?
- **生成功能**：根据编辑后的数据生成Excel文件
- **格式优化**：
  - 表头样式（蓝色背景，白色文字）
  - 自动调整列宽
  - 边框样式
  - 文本换行
- **多页支持**：多页PDF会生成多个工作表
- **下载功能**：支持直接下载Excel文件
- **链接复制**：支持复制Excel文件下载链接

### 7. 历史记录 ?
- **记录内容**：
  - 上传的原始文件信息
  - AI识别的初稿结果
  - 用户校正后的结果
  - 最终生成的Excel文件
- **查看功能**：
  - 查看文件详情
  - 查看识别结果
  - 查看校正结果
  - 预览原始文件
  - 下载Excel文件
- **列表展示**：按时间倒序显示所有历史记录

### 8. UI/UX ?
- **美观设计**：使用Element Plus组件库，现代化UI设计
- **响应式布局**：左右分栏，支持调整大小
- **交互优化**：
  - 加载动画（识别时显示转圈圈）
  - 状态提示（已上传、识别中、已完成、失败）
  - 错误提示
  - 成功提示
- **组件功能**：
  - 文件列表展示
  - 表格编辑器
  - 文件预览器
  - 历史记录表格

## 技术实现

### 后端技术栈
- **框架**：Flask 3.0.0
- **数据库**：SQLite + SQLAlchemy
- **AI模型**：Qwen视觉模型（通过dashscope SDK）
- **文件处理**：
  - pdf2image：PDF转图片
  - Pillow：图片处理
  - openpyxl：Excel生成
- **认证**：bcrypt密码加密

### 前端技术栈
- **框架**：Vue 3.3.4
- **UI库**：Element Plus 2.4.4
- **状态管理**：Pinia 2.1.7
- **路由**：Vue Router 4.2.5
- **HTTP客户端**：Axios 1.6.2
- **构建工具**：Vite 5.0.5

### 项目结构
```
表格提取工具/
├── backend/                 # 后端代码
│   ├── app.py              # Flask主应用（API路由）
│   ├── models.py           # 数据库模型（User, FileRecord）
│   ├── auth.py             # 用户认证（注册、登录）
│   ├── ai_service.py       # AI模型调用（Qwen）
│   ├── file_utils.py       # 文件处理工具
│   ├── excel_utils.py      # Excel生成工具
│   ├── init_db.py          # 数据库初始化
│   ├── requirements.txt    # Python依赖
│   └── uploads/            # 上传文件存储
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   │   ├── Login.vue      # 登录页
│   │   │   ├── Register.vue   # 注册页
│   │   │   ├── Home.vue       # 主页面（上传、识别、编辑）
│   │   │   └── History.vue    # 历史记录页
│   │   ├── stores/        # 状态管理
│   │   │   └── user.js        # 用户状态
│   │   ├── api/           # API调用
│   │   │   └── index.js       # Axios配置
│   │   ├── router/        # 路由配置
│   │   │   └── index.js       # 路由定义
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite配置
├── .env                   # 环境变量（需要创建）
├── .env.example           # 环境变量示例
├── README.md              # 项目说明
├── INSTALL.md             # 安装说明
├── QUICKSTART.md          # 快速启动指南
└── PROJECT_SUMMARY.md     # 本文件
```

## API接口

### 用户相关
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录

### 文件相关
- `POST /api/upload` - 上传文件
- `GET /api/files/<id>/preview` - 预览文件
- `POST /api/files/<id>/recognize` - 识别文件
- `POST /api/files/<id>/correct` - 保存校正数据
- `POST /api/files/<id>/generate-excel` - 生成Excel
- `GET /api/files/<id>/download-excel` - 下载Excel
- `GET /api/files/<id>` - 获取文件详情
- `GET /api/users/<id>/files` - 获取用户所有文件

## 环境配置

### 必需的环境变量（.env文件）
```env
# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# 数据库配置
DATABASE_URL=sqlite:///table_extractor.db

# Qwen API配置（必需）
QWEN_API_KEY=your-api-key
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-vl-max

# 文件上传配置
UPLOAD_FOLDER=backend/uploads
MAX_FILE_SIZE=10485760

# Poppler配置（Windows用户可能需要）
# POPPLER_PATH=C:\poppler\Library\bin

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

## 使用流程

1. **启动后端**：`cd backend && python app.py`
2. **启动前端**：`cd frontend && npm run dev`
3. **访问应用**：http://localhost:5173
4. **注册账号**：创建新账号
5. **上传文件**：拖拽或选择PDF/图片文件
6. **开始识别**：点击"开始识别"按钮
7. **编辑数据**：查看识别结果，编辑校正
8. **生成Excel**：点击"生成Excel"按钮
9. **下载文件**：下载或复制Excel文件链接
10. **查看历史**：在历史记录页面查看所有操作

## 注意事项

1. **Qwen API密钥**：必须配置有效的API密钥才能使用识别功能
2. **Poppler安装**：Windows用户需要安装Poppler才能处理PDF文件
3. **文件大小**：默认限制10MB，可在.env中修改
4. **数据库**：首次运行需要执行`python init_db.py`初始化数据库
5. **端口冲突**：确保5000和5173端口未被占用

## 后续优化建议

1. 添加文件删除功能（历史记录页面）
2. 添加批量下载功能
3. 优化大文件处理性能
4. 添加识别进度百分比显示
5. 支持更多文件格式（Word、Excel等）
6. 添加表格模板功能
7. 支持导出为CSV格式
8. 添加用户权限管理
9. 优化移动端适配
10. 添加数据统计功能

