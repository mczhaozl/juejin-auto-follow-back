# CI/CD 完全指南：持续集成与持续部署实战

> 深入讲解 CI/CD 流程，包括构建、测试、部署自动化，Jenkins、GitLab CI、GitHub Actions 的配置，以及蓝绿部署、金丝雀发布实践。

## 一、CI/CD 基础

### 1.1 什么是 CI/CD

持续集成与持续交付：

```
┌─────────────────────────────────────────────────────────────────┐
│                       CI/CD 流程                                 │
│                                                                 │
│  代码提交  →  构建  →  测试  →  部署  →  监控                  │
│      ↓        ↓        ↓        ↓                              │
│   Git    Docker    Jest    K8s/VM    Prometheus               │
│                                                                 │
│  CI (持续集成)   CD (持续交付/部署)                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| CI | 代码提交自动构建测试 |
| CD | 自动部署到生产环境 |
| Pipeline | 流水线 |
| Artifact | 构建产物 |

## 二、CI 流程

### 2.1 GitHub Actions

```yaml
name: CI

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
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Run tests
        run: npm test
      
      - name: Build
        run: npm run build
```

### 2.2 GitLab CI

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  script:
    - npm test
  coverage: /Coverage: \d+\.\d+%/

deploy:
  stage: deploy
  script:
    - npm run deploy
  only:
    - main
```

### 2.3 Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'npm run deploy'
            }
        }
    }
}
```

## 三、CD 流程

### 3.1 部署配置

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: myapp:latest
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            docker pull myapp:latest
            docker stop myapp || true
            docker rm myapp || true
            docker run -d --name myapp myapp:latest
```

### 3.2 Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    restart: always
```

## 四、部署策略

### 4.1 蓝绿部署

```
阶段1: 蓝绿各一版

┌─────────────┐      ┌─────────────┐
│   Blue v1   │      │  Green v2   │
│  (生产)     │      │  (新版本)   │
│  流量 100%  │      │   流量 0%   │
└─────────────┘      └─────────────┘

阶段2: 切换流量

┌─────────────┐      ┌─────────────┐
│   Blue v1   │      │  Green v2   │
│  (旧版本)   │      │  (生产)     │
│   流量 0%   │      │  流量 100%  │
└─────────────┘      └─────────────┘

阶段3: 回滚

┌─────────────┐      ┌─────────────┐
│   Blue v1   │      │  Green v2   │
│  (生产)     │      │  (新版本)   │
│  流量 100%  │      │   流量 0%   │
└─────────────┘      └─────────────┘
```

### 4.2 金丝雀发布

```yaml
# Kubernetes Canary
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-v1
spec:
  replicas: 10
  selector:
    matchLabels:
      version: v1
  template:
    spec:
      containers:
        - name: myapp
          image: myapp:v1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-canary
spec:
  replicas: 2
  selector:
    matchLabels:
      version: canary
  template:
    spec:
      containers:
        - name: myapp
          image: myapp:v2
```

### 4.3 滚动更新

```yaml
# Kubernetes Rolling Update
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

## 五、测试自动化

### 5.1 单元测试

```yaml
test:
  script:
    - npm test
  coverage: /Coverage: \d+\.\d+%/
  artifacts:
    reports:
      junit: junit.xml
      coverage/cobertura: coverage.xml
```

### 5.2 E2E 测试

```yaml
e2e:
  script:
    - npm run build
    - npm run start &
    - sleep 5
    - npx cypress run
```

## 六、监控与回滚

### 6.1 健康检查

```yaml
health-check:
  script:
    - curl -f http://localhost:3000/health || exit 1
```

### 6.2 自动回滚

```yaml
rollback:
  script: |
    if ! curl -f http://localhost:3000/health; then
      kubectl rollout undo deployment/myapp
      exit 1
    fi
```

## 七、实战案例

### 7.1 完整流程

```yaml
name: Full CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: build
          path: dist
      - name: Deploy
        run: ./deploy.sh
```

## 八、总结

CI/CD 核心要点：

1. **CI**：持续集成
2. **CD**：持续交付/部署
3. **Pipeline**：自动化流水线
4. **测试**：单元/E2E
5. **部署**：蓝绿/金丝雀
6. **回滚**：自动回滚

掌握这些，DevOps so easy！

---

**推荐阅读**：
- [Jenkins 官方文档](https://www.jenkins.io/doc/)
- [GitLab CI 文档](https://docs.gitlab.com/ee/ci/)

**如果对你有帮助，欢迎点赞收藏！**
