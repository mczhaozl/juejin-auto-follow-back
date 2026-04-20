# Docker 多阶段构建完全指南：优化镜像大小与构建流程

## 一、多阶段构建概述

多阶段构建是 Docker 17.05 引入的特性，能显著优化容器镜像大小，简化构建流程。

### 1.1 为什么需要多阶段构建

传统构建方式面临的问题：
- 镜像体积过大，包含构建工具与依赖
- 构建工具与依赖在生产环境不需要
- 安全性隐患（构建工具可能有漏洞）
- 部署与拉取速度慢

### 1.2 多阶段构建的优势

- **镜像最小化**：仅包含运行时所需
- **构建优化**：分层构建，利用缓存
- **安全增强**：移除不必要的工具
- **流程简化**：单 Dockerfile 完成全部工作

---

## 二、基础使用与语法

### 2.1 简单示例

```dockerfile
# 阶段 1：构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 阶段 2：生产阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2.2 AS 别名命名

```dockerfile
# 使用别名
FROM golang:1.22 AS build-stage
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o /app

# 使用 alias
FROM gcr.io/distroless/static-debian12
COPY --from=build-stage /app /app
CMD ["/app"]
```

---

## 三、多阶段构建深入

### 3.1 阶段间文件复制

```dockerfile
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production  # 仅安装生产依赖
RUN npm install -g typescript
COPY tsconfig.json ./
COPY src ./src
RUN tsc

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
USER node
CMD ["node", "dist/index.js"]
```

### 3.2 复制特定文件

```dockerfile
# 从特定阶段复制特定文件
FROM ubuntu:22.04 AS builder
RUN apt-get update && apt-get install -y gcc make
COPY . .
RUN make

FROM alpine:3.19
COPY --from=builder /app/bin/main /usr/local/bin/
COPY --from=builder /app/config/*.yaml /etc/app/
CMD ["main"]
```

---

## 四、缓存优化

### 4.1 分层利用缓存

```dockerfile
FROM node:18 AS deps
WORKDIR /app
# 先复制 package 文件，利用缓存
COPY package*.json ./
RUN npm ci

FROM node:18 AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:18-alpine AS prod
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 4.2 RUN 缓存挂载

```dockerfile
# Docker 18.09+ 支持缓存挂载
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/app/.npm npm ci --cache /app/.npm
COPY . .
RUN npm run build
```

---

## 五、语言特定优化

### 5.1 Go 语言

```dockerfile
# 多阶段 Go 构建
FROM golang:1.22 AS builder
WORKDIR /app
ENV CGO_ENABLED=0
ENV GOOS=linux
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -ldflags="-s -w" -o myapp

# distroless 镜像
FROM gcr.io/distroless/static-debian12
WORKDIR /
COPY --from=builder /app/myapp /myapp
CMD ["/myapp"]
```

### 5.2 Java

```dockerfile
# Maven 多阶段构建
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml ./
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

# 运行阶段
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 5.3 Python

```dockerfile
# Python 多阶段构建
FROM python:3.12 AS builder
WORKDIR /app
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/venv ./venv
ENV PATH="/app/venv/bin:$PATH"
COPY app.py .
CMD ["python", "app.py"]
```

---

## 六、高级技巧

### 6.1 多平台构建

```dockerfile
# 使用 buildx
FROM --platform=$BUILDPLATFORM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM --platform=$TARGETPLATFORM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

### 6.2 命名多个阶段

```dockerfile
FROM node:18 AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM base AS dev
COPY . .
CMD ["npm", "run", "dev"]

FROM base AS build
COPY . .
RUN npm run build

FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
```

### 6.3 使用外部镜像作为源

```dockerfile
FROM alpine:3.19
# 从官方 nginx 复制文件
COPY --from=nginx:alpine /etc/nginx/nginx.conf /etc/nginx/
COPY --from=nginx:alpine /docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
```

---

## 七、最佳实践

### 7.1 优化要点

1. **使用 Alpine 或 Distroless 作为基础**
2. **分离依赖安装与代码构建**
3. **利用多阶段缓存**
4. **移除调试信息**
5. **合并 RUN 命令**

### 7.2 安全性考量

```dockerfile
FROM node:18 AS builder
# ...

FROM node:18-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
WORKDIR /app
COPY --chown=appuser:appgroup --from=builder /app/dist ./dist
```

---

## 八、总结

多阶段构建是优化 Docker 镜像的关键技术，能显著减小体积、提升安全性、优化构建流程。掌握这一技术是容器化开发的必备技能。
