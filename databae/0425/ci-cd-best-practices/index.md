# CI/CD 最佳实践完全指南：从入门到生产

CI/CD 是现代软件开发的核心实践。本文将带你从基础到高级，全面掌握 CI/CD。

## 一、CI/CD 基础

### 1. 什么是 CI/CD

```
CI (Continuous Integration): 持续集成
- 频繁地将代码合并到主干分支
- 自动化构建和测试
- 快速发现和修复问题

CD (Continuous Delivery): 持续交付
- 自动化部署到预发布环境
- 手动确认后部署到生产

CD (Continuous Deployment): 持续部署
- 自动化部署到生产环境
- 无需手动干预
```

### 2. CI/CD 流水线

```
代码提交 → 构建 → 测试 → 代码质量分析 → 安全扫描 → 部署
```

## 二、GitHub Actions

### 1. 基础工作流

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Lint
      run: npm run lint
    
    - name: Test
      run: npm test
    
    - name: Build
      run: npm run build
```

### 2. 多环境部署

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
    - run: npm ci
    - run: npm test

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to staging
      run: |
        echo "Deploying to staging..."
        # 部署脚本

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v4
    - name: Deploy to production
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.PRODUCTION_KEY }}
        script: |
          cd /var/www/app
          git pull
          npm ci
          npm run build
          pm2 restart app
```

### 3. 矩阵构建

```yaml
name: Matrix Build

on: [push]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20, 22]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
    - run: npm ci
    - run: npm test
```

### 4. 缓存依赖

```yaml
name: CI with Cache

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Cache node_modules
      uses: actions/cache@v4
      with:
        path: |
          node_modules
          ~/.npm
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
        restore-keys: |
          ${{ runner.os }}-node-
    
    - name: Install dependencies
      run: npm ci
```

## 三、GitLab CI

### 1. .gitlab-ci.yml

```yaml
stages:
  - build
  - test
  - deploy

variables:
  NODE_VERSION: "20"

build:
  stage: build
  image: node:${NODE_VERSION}
  cache:
    paths:
      - node_modules/
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  image: node:${NODE_VERSION}
  cache:
    paths:
      - node_modules/
  script:
    - npm ci
    - npm test
  coverage: /All files[^|]*\|[^|]*\s+([\d\.]+)/

deploy_staging:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - ssh -o StrictHostKeyChecking=no user@staging.example.com "cd /var/www/app && git pull && npm ci && npm run build"
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy_production:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - ssh -o StrictHostKeyChecking=no user@example.com "cd /var/www/app && git pull && npm ci && npm run build && pm2 restart app"
  environment:
    name: production
    url: https://example.com
  only:
    - main
  when: manual
```

## 四、Docker 集成

### 1. 构建和推送镜像

```yaml
name: Build and Push Docker

on:
  push:
    tags:
      - 'v*'

jobs:
  docker:
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
            type=sha
      
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

### 2. Docker Compose 测试

```yaml
name: Docker Compose Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Start services
        run: docker-compose -f docker-compose.test.yml up -d
      
      - name: Wait for services
        run: |
          for i in {1..30}; do
            if docker-compose -f docker-compose.test.yml exec -T app npm run health-check; then
              break
            fi
            echo "Waiting for services..."
            sleep 2
          done
      
      - name: Run tests
        run: docker-compose -f docker-compose.test.yml exec -T app npm test
      
      - name: Stop services
        if: always()
        run: docker-compose -f docker-compose.test.yml down
```

## 五、代码质量和安全

### 1. ESLint 和 Prettier

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm run format:check
```

### 2. SonarQube

```yaml
name: SonarQube Analysis

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### 3. 依赖安全扫描

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Audit dependencies
        run: npm audit --audit-level=moderate
      
      - name: Snyk Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
      
      - name: Trivy FS Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          ignore-unfixed: true
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
```

## 六、测试策略

### 1. 单元测试

```yaml
name: Unit Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:unit
      - uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
```

### 2. E2E 测试

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Start app
        run: npm run start:test &
      
      - name: Wait for app
        run: npx wait-on http://localhost:3000
      
      - name: Run Cypress
        uses: cypress-io/github-action@v6
        with:
          start: npm run start:test
          wait-on: 'http://localhost:3000'
      
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots
```

## 七、通知和监控

```yaml
name: CI with Notifications

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      
      - name: Slack Notification
        uses: 8398a7/action-slack@v3
        if: always()
        with:
          status: ${{ job.status }}
          text: 'CI ${{ job.status }} for ${{ github.repository }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 八、最佳实践

1. 保持流水线快速（< 10 分钟）
2. 并行执行独立任务
3. 缓存依赖和构建产物
4. 全面的测试策略
5. 代码质量检查
6. 安全扫描
7. 多环境部署
8. 手动审批生产部署
9. 完善的通知机制
10. 监控和日志

## 九、总结

CI/CD 核心要点：
- CI/CD 基础概念
- GitHub Actions 配置
- GitLab CI 配置
- Docker 集成
- 代码质量和安全
- 测试策略
- 通知和监控
- 最佳实践

开始搭建你的 CI/CD 流水线吧！
