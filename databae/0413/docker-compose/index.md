# Docker Compose 完全指南：多容器编排实战

> 深入讲解 Docker Compose，包括服务定义、网络配置、数据卷挂载，以及实际项目中的多容器应用编排和开发环境管理。

## 一、快速开始

### 1.1 安装

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# macOS
brew install docker-compose
```

### 1.2 基础使用

```bash
# 启动所有服务
docker-compose up

# 后台启动
docker-compose up -d

# 停止
docker-compose down
```

## 二、docker-compose.yml

### 2.1 基础配置

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

  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data
```

### 2.2 服务定义

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass password
```

## 三、网络配置

### 3.1 默认网络

```yaml
# 默认创建 app_default 网络
services:
  web:
    build: .
  api:
    build: .
```

### 3.2 自定义网络

```yaml
networks:
  frontend:
  backend:

services:
  web:
    networks:
      - frontend
  db:
    networks:
      - backend
```

## 四、数据卷

### 4.1 命名卷

```yaml
volumes:
  mydata:

services:
  web:
    volumes:
      - mydata:/app/data
```

### 4.2 绑定挂载

```yaml
services:
  web:
    volumes:
      - ./src:/app/src
      - /app/node_modules
```

## 五、实战案例

### 5.1 Node.js + MySQL

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DB_HOST: db
      DB_USER: root
      DB_PASSWORD: secret
    depends_on:
      - db

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: myapp
    volumes:
      - db-data:/var/lib/mysql

volumes:
  db-data:
```

### 5.2 开发环境

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run dev

  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: dev
```

## 六、命令

### 6.1 常用命令

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec web sh

# 重新构建
docker-compose build

# 扩展服务
docker-compose up --scale web=3
```

## 七、总结

Docker Compose 核心要点：

1. **docker-compose.yml**：服务定义
2. **services**：服务配置
3. **networks**：网络配置
4. **volumes**：数据卷
5. **depends_on**：依赖关系
6. **环境变量**：配置管理

掌握这些，多容器部署不再难！

---

**推荐阅读**：
- [Docker Compose 官方文档](https://docs.docker.com/compose/)

**如果对你有帮助，欢迎点赞收藏！**
