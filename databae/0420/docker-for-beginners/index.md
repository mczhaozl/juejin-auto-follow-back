# Docker 入门完全指南：从安装到实战

Docker 是一个开源的容器化平台，让应用部署变得简单、一致、可移植。本文将带你从零开始学习 Docker。

## 一、Docker 简介

### 1. 什么是 Docker

Docker 是一个用于开发、交付和运行应用的开源平台，使用容器技术将应用及其依赖打包在一起。

### 2. 为什么使用 Docker

- **一致性**：开发、测试、生产环境一致
- **轻量级**：容器共享内核，启动快
- **隔离性**：应用之间互不干扰
- **可移植**：一次构建，到处运行
- **版本控制**：镜像版本管理

### 3. Docker vs 虚拟机

| 特性 | Docker | 虚拟机 |
|------|--------|--------|
| 隔离级别 | 进程级 | 硬件级 |
| 启动速度 | 秒级 | 分钟级 |
| 资源占用 | 低 | 高 |
| 镜像大小 | MB 级 | GB 级 |

## 二、安装 Docker

### 1. Windows 安装

下载 Docker Desktop for Windows：https://www.docker.com/products/docker-desktop

### 2. macOS 安装

下载 Docker Desktop for Mac：https://www.docker.com/products/docker-desktop

或使用 Homebrew：
```bash
brew install --cask docker
```

### 3. Linux 安装（Ubuntu）

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置稳定版仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 验证安装
sudo docker --version
sudo docker run hello-world
```

### 4. 验证安装

```bash
# 查看版本
docker --version
docker-compose --version

# 运行 hello-world
docker run hello-world

# 查看 Docker 信息
docker info
```

## 三、Docker 核心概念

### 1. 镜像（Image）

镜像是一个只读的模板，用于创建容器。

```bash
# 搜索镜像
docker search nginx

# 拉取镜像
docker pull nginx
docker pull nginx:latest
docker pull nginx:1.25.0

# 查看本地镜像
docker images
docker image ls

# 删除镜像
docker rmi nginx
docker image rm nginx
```

### 2. 容器（Container）

容器是镜像的运行实例。

```bash
# 运行容器
docker run nginx
docker run -d nginx  # 后台运行
docker run -d -p 80:80 nginx  # 端口映射

# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 停止容器
docker stop container_id

# 启动容器
docker start container_id

# 重启容器
docker restart container_id

# 删除容器
docker rm container_id
docker rm -f container_id  # 强制删除

# 进入容器
docker exec -it container_id /bin/bash
docker exec -it container_id sh

# 查看容器日志
docker logs container_id
docker logs -f container_id  # 实时查看

# 查看容器信息
docker inspect container_id
```

### 3. Dockerfile

Dockerfile 是用于构建镜像的文本文件。

```dockerfile
# Dockerfile 示例
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

### 4. 构建镜像

```bash
# 构建镜像
docker build -t my-app .
docker build -t my-app:v1.0 .
docker build -t my-app:v1.0 -f Dockerfile.prod .

# 查看构建历史
docker history my-app
```

## 四、常用命令实战

### 1. 运行 Nginx

```bash
# 拉取 Nginx 镜像
docker pull nginx

# 运行 Nginx 容器
docker run -d \
  --name my-nginx \
  -p 80:80 \
  -v /path/to/html:/usr/share/nginx/html \
  nginx

# 访问
# http://localhost

# 查看日志
docker logs my-nginx

# 停止容器
docker stop my-nginx

# 删除容器
docker rm my-nginx
```

### 2. 运行 MySQL

```bash
# 拉取 MySQL 镜像
docker pull mysql:8.0

# 运行 MySQL 容器
docker run -d \
  --name my-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=mydb \
  -e MYSQL_USER=user \
  -e MYSQL_PASSWORD=password \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# 连接 MySQL
docker exec -it my-mysql mysql -u root -p

# 或使用 MySQL 客户端
mysql -h 127.0.0.1 -P 3306 -u root -p
```

### 3. 运行 Redis

```bash
# 拉取 Redis 镜像
docker pull redis:7-alpine

# 运行 Redis 容器
docker run -d \
  --name my-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes

# 连接 Redis
docker exec -it my-redis redis-cli

# 测试
> set key value
> get key
```

### 4. 运行 Node.js 应用

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

USER node

CMD ["node", "server.js"]
```

```javascript
// server.js
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello from Docker!');
});

app.listen(port, '0.0.0.0', () => {
  console.log(`App running on http://0.0.0.0:${port}`);
});
```

```json
{
  "name": "docker-demo",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

```bash
# 构建镜像
docker build -t node-app .

# 运行容器
docker run -d \
  --name node-app \
  -p 3000:3000 \
  node-app

# 访问
# http://localhost:3000
```

## 五、Docker Compose

### 1. 什么是 Docker Compose

Docker Compose 用于定义和运行多容器 Docker 应用。

### 2. docker-compose.yml 示例

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
      - redis
    environment:
      - DB_HOST=db
      - REDIS_HOST=redis

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: mydb
    volumes:
      - db-data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

volumes:
  db-data:
  redis-data:
```

### 3. Docker Compose 命令

```bash
# 启动所有服务
docker-compose up
docker-compose up -d  # 后台运行

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs
docker-compose logs -f

# 重启服务
docker-compose restart

# 构建并启动
docker-compose up --build

# 停止并删除容器、网络、卷
docker-compose down -v
```

## 六、数据管理

### 1. 卷（Volumes）

```bash
# 创建卷
docker volume create my-volume

# 查看卷
docker volume ls

# 查看卷详情
docker volume inspect my-volume

# 使用卷
docker run -d -v my-volume:/app/data nginx

# 删除卷
docker volume rm my-volume

# 删除未使用的卷
docker volume prune
```

### 2. 绑定挂载（Bind Mounts）

```bash
# 绑定挂载
docker run -d -v /host/path:/container/path nginx

# 只读挂载
docker run -d -v /host/path:/container/path:ro nginx
```

## 七、网络管理

### 1. 网络类型

```bash
# 查看网络
docker network ls

# 创建网络
docker network create my-network

# 连接容器到网络
docker network connect my-network container1
docker network connect my-network container2

# 断开容器
docker network disconnect my-network container1

# 删除网络
docker network rm my-network

# 使用网络
docker run -d --network my-network --name app1 nginx
docker run -d --network my-network --name app2 nginx

# 容器之间可以通过名称访问
# app1 可以 ping app2
```

## 八、最佳实践

### 1. Dockerfile 最佳实践

```dockerfile
# 使用官方基础镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，利用缓存
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 3000

# 使用非 root 用户
USER node

# 启动命令
CMD ["node", "server.js"]
```

### 2. 多阶段构建

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --only=production
EXPOSE 3000
USER node
CMD ["node", "dist/server.js"]
```

## 九、总结

Docker 是现代应用开发和部署的重要工具。通过本文的学习，你应该已经掌握了：

1. Docker 的安装和基本概念
2. 常用的 Docker 命令
3. Dockerfile 的编写
4. Docker Compose 的使用
5. 数据管理和网络管理
6. 最佳实践

继续实践，深入学习 Docker！

## 参考资料

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Awesome Docker](https://github.com/veggiemonk/awesome-docker)
