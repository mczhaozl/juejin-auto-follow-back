# CI/CD 流水线实战：GitHub Actions 与自动化部署

> 手把手教你搭建 CI/CD 流水线，包括 GitHub Actions 基础、自动化测试、Docker 镜像构建和自动部署到生产环境。

## 一、CI/CD 概念

### 1.1 什么是 CI/CD

```
开发 → 提交代码 → 自动构建 → 自动测试 → 自动部署
```

| 阶段 | 说明 |
|------|------|
| CI | 持续集成，自动构建和测试 |
| CD | 持续交付，自动部署到测试环境 |
| CD | 持续部署，自动部署到生产环境 |

## 二、GitHub Actions

### 2.1 基础结构

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: Install Dependencies
        run: npm ci
        
      - name: Run Tests
        run: npm test
```

### 2.2 触发条件

```yaml
on:
  push:
    branches: [main, develop]
    tags: ['v*']
    paths: ['src/**', '*.js']
  pull_request:
    branches: [main]
  workflow_dispatch:  # 手动触发
  schedule:
    - cron: '0 0 * * *'  # 定时任务
```

## 三、自动化测试

### 3.1 运行测试

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install
        run: npm ci
        
      - name: Lint
        run: npm run lint
        
      - name: Test
        run: npm test
        
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

### 3.2 矩阵测试

```yaml
jobs:
  test:
    strategy:
      matrix:
        node-version: [16, 18, 20]
        os: [ubuntu-latest, windows-latest]
        
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          
      - run: npm ci
      - run: npm test
```

## 四、Docker 构建

### 4.1 构建镜像

```yaml
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
          
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: user/app:${{ github.sha }}
```

### 4.2 多平台构建

```yaml
- name: Build
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: user/app:latest
```

## 五、自动部署

### 5.1 部署到服务器

```yaml
jobs:
  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to Server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app
            docker-compose pull
            docker-compose up -d
```

### 5.2 部署到云

```yaml
# AWS
- name: Deploy to AWS
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Deploy to ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: task-definition.json
    service: my-service
    cluster: my-cluster
```

## 六、缓存优化

### 6.1 npm 缓存

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'
```

### 6.2 Docker 缓存

```yaml
- name: Build
  uses: docker/build-push-action@v5
  with:
    context: .
    push: false
    load: true
    cache-from: type=registry,ref=user/app:buildcache
    cache-to: type=registry,ref=user/app:buildcache,mode=max
```

## 七、总结

CI/CD 核心要点：

1. **触发条件**：push、PR、定时
2. **自动化测试**：Lint + Unit + E2E
3. **Docker 构建**：多平台、缓存
4. **自动部署**：SSH、云服务
5. **环境管理**：dev、staging、prod

自动化是效率的关键，CI/CD 必备！

---

**推荐阅读**：
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Actions 市场](https://github.com/marketplace)

**如果对你有帮助，欢迎点赞收藏！**
