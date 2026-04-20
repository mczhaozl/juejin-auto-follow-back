# GitHub Actions 矩阵构建与并行测试完全指南

## 一、矩阵构建概述

### 1.1 什么是矩阵构建

使用多个配置组合运行同一个 job，实现并行测试。

### 1.2 优势

- 快速测试多版本
- 并行执行节省时间
- 保证兼容性

---

## 二、基本矩阵

### 2.1 单维度矩阵

```yaml
name: Build
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

### 2.2 多维度矩阵

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

---

## 三、矩阵配置

### 3.1 包含组合

```yaml
strategy:
  matrix:
    os: [ubuntu-latest]
    node-version: [18, 20]
    include:
      - os: macos-latest
        node-version: 20
      - os: windows-latest
        node-version: 20
```

### 3.2 排除组合

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node-version: [16, 18, 20]
    exclude:
      - os: windows-latest
        node-version: 16
      - os: macos-latest
        node-version: 16
```

### 3.3 快速失败

```yaml
strategy:
  fail-fast: true
  matrix:
    node-version: [18, 20, 22]
```

---

## 四、高级用法

### 4.1 矩阵对象

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        version: 18
        env: dev
      - os: ubuntu-latest
        version: 20
        env: prod
```

### 4.2 环境变量

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        include:
          - os: ubuntu-latest
            compiler: gcc
          - os: windows-latest
            compiler: msvc
    env:
      CC: ${{ matrix.compiler }}
    steps:
      - run: echo $CC
```

### 4.3 使用 JSON

```yaml
strategy:
  matrix:
    node:
      - version: 18
        npm: 9
      - version: 20
        npm: 10
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node.version }}
```

---

## 五、实战示例

### 5.1 多浏览器测试

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chrome, firefox, safari]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm test -- --browser ${{ matrix.browser }}
```

### 5.2 多数据库测试

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        database: [postgres, mysql, sqlite]
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        if: matrix.database == 'postgres'
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test -- --db ${{ matrix.database }}
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/postgres
```

### 5.3 构建矩阵

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        arch: [amd64, arm64]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          platforms: linux/${{ matrix.arch }}
          push: true
          tags: myimage:latest-${{ matrix.arch }}
```

---

## 六、缓存策略

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

---

## 七、最佳实践

- 从简单矩阵开始
- 使用 fail-fast 快速反馈
- 合理利用缓存
- 监控执行时间
- 考虑成本限制

---

## 总结

矩阵构建是 GitHub Actions 的强大功能，可以高效地在多个环境中测试和构建，提升软件质量。
