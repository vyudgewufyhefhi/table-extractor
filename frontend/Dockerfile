# 前端 Dockerfile - 多阶段构建
# 阶段1: 构建
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
# 注意：在 Docker 环境中，前端通过 nginx 代理到后端
# 所以 VITE_API_URL 应该为空（使用相对路径 /api）
# 如果需要自定义 API 地址，可以通过 ARG 传递
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# 阶段2: 运行
FROM nginx:alpine

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]

