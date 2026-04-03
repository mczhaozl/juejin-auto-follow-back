# Docker 容器化最佳实践完全指南

Docker 已成为现代应用部署的标准。本文将带你全面掌握 Docker 容器化的最佳实践。

## 一、Dockerfile 最佳实践

### 1. 选择基础镜像

```dockerfile
# ❌ 不好：使用过大的基础镜像
FROM ubuntu:latest

# ✅ 好：使用轻量级镜像
FROM node:20-slim
FROM python:3.12-slim
FROM alpine:3.19

# 更好：使用多阶段构建
```

### 2. 多阶段构建

```dockerfile
# 构建阶段
FROM node:20 AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:1.25-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. 层缓存优化

```dockerfile
FROM node:20-slim

WORKDIR /app

# 先复制依赖文件，利用缓存
COPY package*.json ./
RUN npm ci

# 再复制源码
COPY . .

RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### 4. 最小化镜像

```dockerfile
# 使用 Alpine
FROM alpine:3.19

RUN apk add --no-cache nodejs npm

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]

# 清理缓存
RUN npm cache clean --force && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*
```

### 5. 非 root 用户

```dockerfile
FROM node:20-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY --chown=appuser:appuser package*.json ./
RUN npm ci --only=production

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 3000
CMD ["node", "server.js"]
```

### 6. .dockerignore

```
node_modules
npm-debug.log
.git
.gitignore
.env
.env.local
dist
build
coverage
*.md
!README.md
.DS_Store
.vscode
.idea
```

## 二、镜像优化

### 1. 减小镜像体积

```dockerfile
# 合并 RUN 命令
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# 使用 --no-install-recommends
RUN apk add --no-cache curl git

# 多阶段构建
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o main .

FROM scratch
COPY --from=builder /app/main /main
CMD ["/main"]
```

### 2. 镜像标签

```bash
# 构建并标记
docker build -t myapp:latest .
docker build -t myapp:v1.0.0 .
docker build -t myapp:v1.0 .
docker build -t myapp:20240425 .

# 使用 Git commit hash
docker build -t myapp:$(git rev-parse --short HEAD) .
```

## 三、容器运行时最佳实践

### 1. 资源限制

```bash
# 限制 CPU 和内存
docker run -d \
  --name myapp \
  --cpus="1.0" \
  --memory="512m" \
  --memory-swap="512m" \
  myapp:latest

# docker-compose.yml
version: '3.8'
services:
  app:
    image: myapp:latest
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 2. 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# docker-compose.yml
services:
  app:
    image: myapp:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 3. 日志管理

```bash
# 配置日志驱动
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  myapp:latest

# docker-compose.yml
services:
  app:
    image: myapp:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. 数据持久化

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  app:
    image: myapp:latest
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

volumes:
  postgres_data:
```

## 四、Docker Compose

### 1. 开发环境

```yaml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      db:
        condition: service_healthy
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
          ignore:
            - node_modules/
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 2. 生产环境

```yaml
version: '3.8'
services:
  app:
    image: myapp:v1.0.0
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      placement:
        constraints:
          - node.role == manager
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
  
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    deploy:
      mode: global

volumes:
  postgres_data:
  redis_data:
```

## 五、安全最佳实践

### 1. 扫描漏洞

```bash
# 使用 Trivy
trivy image myapp:latest

# 使用 Docker Scan
docker scan myapp:latest

# 使用 Clair
clair-scanner myapp:latest
```

### 2. 最小化攻击面

```dockerfile
# 非 root 用户
USER appuser

# 只读文件系统
docker run --read-only --tmpfs /tmp myapp:latest

# 禁用不必要的能力
docker run --cap-drop all --cap-add NET_BIND_SERVICE myapp:latest

# Seccomp 配置
docker run --security-opt seccomp=seccomp.json myapp:latest
```

### 3. 机密管理

```yaml
version: '3.8'
services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

## 六、CI/CD 集成

```yaml
# .github/workflows/docker.yml
name: Build and Push Docker

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: username/myapp
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## 七、最佳实践总结

1. 使用多阶段构建减小镜像
2. 选择轻量级基础镜像
3. 优化层缓存
4. 使用非 root 用户
5. 配置健康检查
6. 限制容器资源
7. 配置日志管理
8. 安全扫描
9. 使用 .dockerignore
10. 正确使用 Docker Compose

## 八、总结

Docker 容器化核心要点：
- Dockerfile 最佳实践
- 镜像优化（多阶段、轻量级）
- 容器运行时（资源限制、健康检查）
- Docker Compose（开发/生产）
- 安全最佳实践
- CI/CD 集成

开始用 Docker 容器化你的应用吧！
