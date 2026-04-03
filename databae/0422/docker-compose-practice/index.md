# Docker Compose 实战完全指南：从开发到生产环境

Docker Compose 是定义和运行多容器 Docker 应用的工具。本文将带你从基础到实战，全面掌握 Docker Compose。

## 一、Docker Compose 基础

### 1. 什么是 Docker Compose

Docker Compose 让你可以用一个 YAML 文件配置所有服务，然后一键启动。

### 2. 安装

```bash
# Docker Desktop 已包含 Compose
docker compose version

# 旧版本
docker-compose version
```

### 3. 基本命令

```bash
# 启动所有服务
docker compose up

# 后台启动
docker compose up -d

# 停止所有服务
docker compose down

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs
docker compose logs -f

# 执行命令
docker compose exec web bash

# 重启服务
docker compose restart web

# 构建镜像
docker compose build
```

## 二、docker-compose.yml 文件结构

### 1. 基础结构

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 2. 常用配置项

```yaml
services:
  app:
    # 镜像
    image: node:18-alpine
    
    # 构建
    build:
      context: .
      dockerfile: Dockerfile
      args:
        NODE_ENV: development
    
    # 端口映射
    ports:
      - "3000:3000"
      - "127.0.0.1:3001:3001"
    
    # 环境变量
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    
    # 环境变量文件
    env_file:
      - .env
      - .env.local
    
    # 卷
    volumes:
      - ./src:/app/src
      - node_modules:/app/node_modules
      - ./config:/app/config:ro
    
    # 依赖
    depends_on:
      - db
      - redis
    
    # 健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    
    # 重启策略
    restart: unless-stopped
    
    # 资源限制
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    
    # 网络
    networks:
      - frontend
      - backend

networks:
  frontend:
  backend:

volumes:
  node_modules:
```

## 三、实战：Web 应用栈

### 1. 完整示例

```yaml
version: '3.8'

services:
  # 前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    depends_on:
      - backend
    networks:
      - frontend
    restart: unless-stopped

  # 后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://user:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - frontend
      - backend
    restart: unless-stopped

  # 数据库
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # 缓存
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - backend
    restart: unless-stopped

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - frontend
    restart: unless-stopped

networks:
  frontend:
  backend:

volumes:
  postgres_data:
  redis_data:
```

### 2. 对应的 Dockerfile

#### frontend/Dockerfile
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### backend/Dockerfile
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

## 四、开发环境配置

### 1. 开发 vs 生产

```yaml
# docker-compose.yml (基础配置)
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
```

```yaml
# docker-compose.override.yml (开发环境)
version: '3.8'
services:
  app:
    volumes:
      - ./src:/app/src
    environment:
      - NODE_ENV=development
    command: npm run dev
```

```yaml
# docker-compose.prod.yml (生产环境)
version: '3.8'
services:
  app:
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
```

### 2. 使用

```bash
# 开发环境（默认使用 override）
docker compose up

# 生产环境
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 五、多环境管理

### 1. .env 文件

```bash
# .env
COMPOSE_PROJECT_NAME=myapp
NODE_ENV=development
PORT=3000
DB_PASSWORD=secret
```

### 2. 不同环境的 .env

```bash
# .env.development
NODE_ENV=development
DEBUG=true

# .env.staging
NODE_ENV=staging
DEBUG=false

# .env.production
NODE_ENV=production
DEBUG=false
```

```bash
docker compose --env-file .env.development up
```

## 六、常用技巧

### 1. 只启动特定服务

```bash
docker compose up -d db redis
```

### 2. 查看特定服务日志

```bash
docker compose logs -f backend
```

### 3. 进入容器

```bash
docker compose exec db psql -U user -d mydb
docker compose run --rm backend bash
```

### 4. 清理

```bash
docker compose down
docker compose down -v  # 删除卷
docker compose down --rmi all  # 删除镜像
docker system prune -a  # 清理所有未使用的
```

## 七、最佳实践

1. 使用 .dockerignore
2. 多阶段构建减小镜像
3. 用卷持久化数据
4. 配置健康检查
5. 合理设置重启策略
6. 用网络隔离服务
7. 限制资源使用
8. 秘密不要提交到代码库

## 八、总结

Docker Compose 让多容器应用管理变得简单：
- 一个 YAML 文件定义所有服务
- 一键启动开发环境
- 便于多环境管理
- 支持生产部署

开始使用 Docker Compose，提升你的开发效率！
