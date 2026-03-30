# GitHub Actions 完全指南：CI/CD 自动化实战

> 深入讲解 GitHub Actions，包括工作流配置、Actions 使用、Secrets 管理，以及实际项目中的 CI/CD 流程设计和部署实践。

## 一、基础概念

### 1.1 工作流

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
      - name: Run tests
        run: npm test
```

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Workflow | 工作流 |
| Job | 作业 |
| Step | 步骤 |
| Action | 动作 |
| Runner | 运行器 |

## 二、触发条件

### 2.1 分支触发

```yaml
on:
  push:
    branches:
      - main
      - 'feature/*'
  pull_request:
    branches: [main]
```

### 2.2 路径触发

```yaml
on:
  push:
    paths:
      - 'src/**'
      - '*.js'
```

### 2.3 定时触发

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
```

## 三、Jobs

### 3.1 多作业

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build

  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - run: npm test
```

### 3.2 矩阵构建

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [14, 16, 18]
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

## 四、Actions

### 4.1 常用 Actions

```yaml
steps:
  - uses: actions/checkout@v4
  
  - uses: actions/setup-node@v4
    with:
      node-version: '18'
      cache: 'npm'
      
  - uses: actions/cache@v3
    with:
      path: ~/.npm
      key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
```

### 4.2 市场 Actions

```yaml
- uses: actions/github-script@v7
  with:
    script: |
      console.log('Hello');
```

## 五、环境变量

### 5.1 设置变量

```yaml
env:
  NODE_ENV: production

jobs:
  build:
    env:
      DB_HOST: localhost
    runs-on: ubuntu-latest
    steps:
      - run: echo $DB_HOST
```

### 5.2 Secrets

```yaml
steps:
  - name: Deploy
    run: deploy.sh
    env:
      API_TOKEN: ${{ secrets.API_TOKEN }}
```

## 六、实战案例

### 6.1 Node.js CI

```yaml
name: Node.js CI

on: [push]

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

### 6.2 自动部署

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
      
      - name: Deploy
        run: |
          echo "Deploying..."
```

## 七、总结

GitHub Actions 核心要点：

1. **Workflow**：工作流配置
2. **触发条件**：push/pull/schedule
3. **Jobs**：作业编排
4. **Actions**：复用动作
5. **Secrets**：敏感信息

掌握这些，CI/CD 自动化 so easy！

---

**推荐阅读**：
- [GitHub Actions 官方文档](https://docs.github.com/en/actions)

**如果对你有帮助，欢迎点赞收藏！**
