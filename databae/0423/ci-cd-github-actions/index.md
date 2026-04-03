# GitHub Actions 完全指南：从零构建 CI/CD 流水线

GitHub Actions 是 GitHub 提供的 CI/CD 服务，可以自动化你的软件开发生命周期。本文将带你全面掌握 GitHub Actions。

## 一、GitHub Actions 基础

### 1. 核心概念

```
Workflow (工作流): 自动化流程的完整定义
Event (事件): 触发工作流的事件
Job (作业): 一系列步骤的集合
Step (步骤): 单个任务
Action (动作): 可复用的单元
Runner (运行器): 执行工作流的服务器
```

### 2. 第一个 Workflow

```yaml
# .github/workflows/hello-world.yml
name: Hello World

on: [push]

jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Hello World
        run: echo "Hello, GitHub Actions!"
```

## 二、Workflow 语法

### 1. 触发事件

```yaml
name: Events Demo

on:
  # 代码推送
  push:
    branches:
      - main
      - develop
    tags:
      - 'v*'
    paths:
      - 'src/**'
      - '!src/docs/**'
  
  # Pull Request
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
  
  # 定时触发
  schedule:
    - cron: '0 0 * * *' # 每天 UTC 0 点
  
  # 手动触发
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
```

### 2. Jobs 配置

```yaml
name: Jobs Demo

on: push

jobs:
  job1:
    name: First Job
    runs-on: ubuntu-latest
    steps:
      - run: echo "Job 1"
  
  job2:
    name: Second Job
    runs-on: ubuntu-latest
    needs: job1 # 依赖 job1
    steps:
      - run: echo "Job 2"
  
  job3:
    name: Parallel Job
    runs-on: ubuntu-latest
    steps:
      - run: echo "Job 3"
  
  matrix:
    name: Matrix Job
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20, 22]
    steps:
      - run: echo "OS: ${{ matrix.os }}, Node: ${{ matrix.node-version }}"
```

### 3. Steps 配置

```yaml
name: Steps Demo

on: push

jobs:
  steps-demo:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run a script
        run: |
          echo "Hello"
          echo "World"
      
      - name: Use an action
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Conditional step
        if: github.ref == 'refs/heads/main'
        run: echo "This is main branch"
      
      - name: Continue on error
        continue-on-error: true
        run: exit 1
      
      - name: Timeout
        timeout-minutes: 5
        run: sleep 600
```

## 三、环境变量与密钥

### 1. 环境变量

```yaml
name: Environment Variables

on: push

env:
  GLOBAL_VAR: "This is global"

jobs:
  env-demo:
    runs-on: ubuntu-latest
    env:
      JOB_VAR: "This is job level"
    steps:
      - name: Print variables
        env:
          STEP_VAR: "This is step level"
        run: |
          echo "Global: $GLOBAL_VAR"
          echo "Job: $JOB_VAR"
          echo "Step: $STEP_VAR"
          echo "GitHub: $GITHUB_REPOSITORY"
```

### 2. 密钥管理

```yaml
name: Secrets Demo

on: push

jobs:
  secrets-demo:
    runs-on: ubuntu-latest
    steps:
      - name: Use secret
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: |
          echo "API Key is set"
          echo "::add-mask::$API_KEY" # 掩码输出
```

### 3. GitHub Context

```yaml
name: Context Demo

on: push

jobs:
  context-demo:
    runs-on: ubuntu-latest
    steps:
      - name: Print context
        run: |
          echo "Repository: ${{ github.repository }}"
          echo "Branch: ${{ github.ref }}"
          echo "Commit: ${{ github.sha }}"
          echo "Actor: ${{ github.actor }}"
          echo "Event: ${{ github.event_name }}"
          
      - name: Dump context
        uses: actions/github-script@v7
        with:
          script: |
            console.log(context)
```

## 四、实战：Node.js 项目

```yaml
name: Node.js CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    name: Build and Test
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18, 20, 22]
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Type check
        run: npm run type-check
      
      - name: Test
        run: npm test
        env:
          CI: true
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.node-version == '20'
        with:
          files: ./coverage/lcov.info
          token: ${{ secrets.CODECOV_TOKEN }}
```

## 五、实战：Docker 构建与部署

```yaml
name: Docker Build and Deploy

on:
  push:
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
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
  
  deploy:
    name: Deploy to Production
    needs: build-and-push
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            docker pull ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            docker stop my-app || true
            docker rm my-app || true
            docker run -d --name my-app -p 80:3000 ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

## 六、实战：发布到 npm

```yaml
name: Publish to npm

on:
  push:
    tags: ['v*']

jobs:
  publish:
    name: Publish to npm
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build
        run: npm run build
      
      - name: Publish
        run: npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
```

## 七、实战：多环境部署

```yaml
name: Deploy to Multiple Environments

on:
  push:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        description: Environment to deploy
        options:
          - staging
          - production
        required: true

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment || (github.ref == 'refs/heads/main' && 'production' || 'staging') }}
      url: ${{ steps.deploy.outputs.url }}
    
    outputs:
      url: ${{ steps.deploy.outputs.url }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          NODE_ENV: ${{ inputs.environment || (github.ref == 'refs/heads/main' && 'production' || 'staging') }}
      
      - name: Deploy
        id: deploy
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

## 八、常用 Actions

### 1. actions/checkout

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    repository: ${{ github.repository }}
    ref: ${{ github.ref }}
    fetch-depth: 0 # 完整历史
    submodules: true # 子模块
    token: ${{ secrets.GITHUB_TOKEN }}
```

### 2. actions/setup-node

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    node-version-file: '.nvmrc'
    cache: 'npm'
    cache-dependency-path: '**/package-lock.json'
    registry-url: 'https://registry.npmjs.org'
```

### 3. actions/cache

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### 4. actions/upload-artifact

```yaml
- name: Upload build artifact
  uses: actions/upload-artifact@v4
  with:
    name: build
    path: build/
    retention-days: 30
```

### 5. actions/download-artifact

```yaml
- name: Download build artifact
  uses: actions/download-artifact@v4
  with:
    name: build
    path: build/
```

## 九、Workflow 复用

### 1. Reusable Workflows

```yaml
# .github/workflows/build.yml
name: Reusable Build Workflow

on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      npm-token:
        required: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build
```

```yaml
# 使用 reusable workflow
name: Use Reusable Workflow

on: push

jobs:
  call-build:
    uses: ./.github/workflows/build.yml
    with:
      node-version: '20'
    secrets:
      npm-token: ${{ secrets.NPM_TOKEN }}
```

### 2. Composite Actions

```yaml
# .github/actions/setup-and-test/action.yml
name: 'Setup and Test'
description: 'Setup Node.js, install dependencies, and test'

inputs:
  node-version:
    description: 'Node.js version'
    required: true
    default: '20'

runs:
  using: 'composite'
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
      shell: bash
    
    - name: Test
      run: npm test
      shell: bash
```

```yaml
# 使用 composite action
name: Use Composite Action

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-and-test
        with:
          node-version: '20'
```

## 十、最佳实践

1. 保持 Workflow 简单明了
2. 使用缓存加速构建
3. 合理使用矩阵构建
4. 保护敏感信息
5. 添加超时设置
6. 使用 Artifacts 传递文件
7. 复用 Workflow 和 Action
8. 添加有意义的名称
9. 测试 Workflow
10. 监控和调试

## 十一、总结

GitHub Actions 核心：
- 理解 Workflow 语法
- 掌握常用事件和触发器
- 使用 Actions 简化配置
- 构建 CI/CD 流水线
- 多环境部署
- 复用 Workflow
- 遵循最佳实践

开始用 GitHub Actions 自动化你的开发流程！
