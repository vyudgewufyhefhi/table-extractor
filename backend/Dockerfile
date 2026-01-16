# 后端 Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（包括 wget 用于健康检查）
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads/excel instance

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]

