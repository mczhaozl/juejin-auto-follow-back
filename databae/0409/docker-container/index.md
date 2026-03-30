# Docker 容器实战：从入门到生产环境部署

> 手把手教你掌握 Docker 核心概念，包括镜像、容器、网络、存储，以及 Docker Compose 编排和 CI/CD 集成。

## 一、Docker 基础概念

### 1.1 什么是 Docker

Docker 是轻量级容器化平台：

```bash
# 运行一个容器
docker run -d -p 80:80 nginx
```

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Image | 镜像，模板 |
| Container | 容器，运行实例 |
| Volume | 存储卷 |
| Network | 网络 |

## 二、Docker 命令

### 2.1 镜像操作

```bash
# 拉取镜像
docker pull nginx:latest

# 查看镜像
docker images

# 删除镜像
docker rmi nginx:latest

# 构建镜像
docker build -t myapp .
```

### 2.2 容器操作

```bash
# 运行容器
docker run -d -p 8080:80 --name mynginx nginx

# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 停止/启动容器
docker stop mynginx
docker start mynginx

# 删除容器
docker rm mynginx

# 进入容器
docker exec -it mynginx bash

# 查看日志
docker logs -f mynginx
```

## 三、Dockerfile 最佳实践

### 3.1 基础 Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

### 3.2 多阶段构建

```dockerfile
# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3.3 .dockerignore

```
node_modules
dist
.git
*.md
.env
```

## 四、Docker Compose

### 4.1 docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=secret

  redis:
    image: redis:7-alpine

volumes:
  db-data:
```

### 4.2 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

## 五、网络配置

### 5.1 自定义网络

```bash
# 创建网络
docker network create mynetwork

# 运行容器并加入网络
docker run -d --network mynetwork --name app1 myapp

# 容器间通信
docker exec app1 ping app2
```

### 5.2 端口映射

```bash
# 主机端口 8080 映射到容器端口 80
docker run -p 8080:80 nginx

# UDP 端口
docker run -p 5353:5353/udp myapp
```

## 六、数据持久化

### 6.1 Volume

```bash
# 创建卷
docker volume create mydata

# 使用卷
docker run -v mydata:/app/data myapp
```

### 6.2 Bind Mount

```bash
# 挂载主机目录
docker run -v $(pwd):/app myapp

# 只读挂载
docker run -v $(pwd):/app:ro myapp
```

## 七、生产环境最佳实践

### 7.1 安全建议

```dockerfile
# 创建非 root 用户
FROM node:18-alpine
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

USER appuser
```

### 7.2 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/ || exit 1
```

### 7.3 资源限制

```bash
docker run -m 512m --cpus=1.5 myapp
```

## 八、总结

Docker 核心要点：

1. **镜像**：模板，只读
2. **容器**：运行实例
3. **Dockerfile**：构建镜像
4. **Compose**：多容器编排
5. **网络/卷**：通信和存储

掌握这些，你就能玩转 Docker！

---

**推荐阅读**：
- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

**如果对你有帮助，欢迎点赞收藏！**
