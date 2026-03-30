# Docker 高级完全指南：网络、存储与 Compose

> 深入讲解 Docker 高级特性，包括 Docker 网络、存储卷、多阶段构建、安全加固，以及实际项目中的容器编排和性能优化。

## 一、Docker 网络

### 1.1 网络驱动

```bash
# 查看网络
docker network ls

# 创建网络
docker network create my-network

# 容器连接到网络
docker network connect my-network container1

# 查看网络详情
docker network inspect my-network
```

### 1.2 网络类型

```yaml
# bridge（默认）
bridge:
  driver: bridge

# host
host:
  driver: host

# overlay（Swarm）
overlay:
  driver: overlay
```

### 1.3 网络配置

```yaml
# docker-compose.yml
services:
  app:
    networks:
      - frontend
      - backend
      
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

## 二、存储卷

### 2.1 卷类型

```bash
# 命名卷
docker volume create my-volume
docker run -v my-volume:/data container

# 绑定挂载
docker run -v /host/path:/container/path container

# tmpfs（内存）
docker run --tmpfs /tmp container
```

### 2.2 卷管理

```bash
# 查看卷
docker volume ls

# 详情
docker volume inspect my-volume

# 删除未使用
docker volume prune
```

### 2.3 Compose 卷

```yaml
volumes:
  db-data:
    driver: local
    
  app-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /host/path
```

## 三、多阶段构建

### 3.1 基础多阶段

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 3.2 Go 示例

```dockerfile
# 构建
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o app .

# 运行
FROM alpine
WORKDIR /app
COPY --from=builder /app/app .
CMD ["./app"]
```

## 四、安全加固

### 4.1 非 root 用户

```dockerfile
FROM node:18-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

### 4.2 安全选项

```bash
# 只读文件系统
docker run --read-only image

# 限制内存
docker run --memory=512m image

# 限制 CPU
docker run --cpus=1.5 image

# 禁止特权
docker run --privileged=false image
```

### 4.2 镜像安全扫描

```bash
# Docker Scout
docker scout cves myimage

# Trivy
trivy image myimage
```

## 五、Dockerfile 最佳实践

### 5.1 优化技巧

```dockerfile
# 1. 使用 Alpine 基础镜像
FROM node:18-alpine

# 2. 按顺序放置指令（变化少的在前）
COPY package*.json ./
RUN npm ci --only=production

# 3. 复制必要文件
COPY . .

# 4. 使用 .dockerignore
# node_modules
.git
*.md
```

### 5.2 .dockerignore

```
# 版本控制
.git
.gitignore

# 构建产物
dist
build

# 依赖
node_modules
npm-debug.log

# 文档
README.md
*.md
```

## 六、Docker Compose

### 6.1 基础配置

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret

  redis:
    image: redis:7-alpine

volumes:
  db-data:
```

### 6.2 扩展配置

```yaml
services:
  app:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
```

## 七、总结

Docker 高级核心要点：

1. **网络**：bridge/host/overlay
2. **存储**：卷/绑定挂载
3. **多阶段构建**：减小镜像
4. **安全**：非 root/资源限制
5. **Compose**：编排工具
6. **.dockerignore**：优化构建

掌握这些，Docker 进阶 so easy！

---

**推荐阅读**：
- [Docker 官方文档](https://docs.docker.com/)

**如果对你有帮助，欢迎点赞收藏！**
