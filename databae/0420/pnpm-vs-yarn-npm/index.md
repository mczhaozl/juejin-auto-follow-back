# PNPM vs Yarn vs npm：JavaScript 包管理器全面对比

JavaScript 生态中有三大主要的包管理器：npm、Yarn 和 pnpm。本文将深入对比这三者的特点、性能和适用场景。

## 一、包管理器概述

### 1. npm（Node Package Manager）

npm 是 Node.js 的默认包管理器，也是最早出现的包管理器之一。

**特点：**
- 官方默认，生态最丰富
- 简单易用，学习成本低
- 版本控制完善

### 2. Yarn

Yarn 由 Facebook、Google、Exponent 和 Tilde 联合开发，旨在解决 npm 的一些问题。

**特点：**
- 更快的安装速度
- 确定性的依赖解析
- 离线模式支持

### 3. pnpm（Performant npm）

pnpm 是一个快速、节省磁盘空间的包管理器，使用硬链接和符号链接来节省空间。

**特点：**
- 极快的安装速度
- 节省磁盘空间
- 严格的依赖管理

## 二、安装方式对比

### 1. npm

```bash
# 随 Node.js 一起安装
node -v
npm -v

# 更新 npm
npm install -g npm@latest

# 查看 npm 配置
npm config list
```

### 2. Yarn

```bash
# 使用 npm 安装
npm install -g yarn

# 使用 Homebrew 安装（macOS）
brew install yarn

# 查看版本
yarn -v

# 查看 Yarn 配置
yarn config list
```

### 3. pnpm

```bash
# 使用 npm 安装
npm install -g pnpm

# 使用 Homebrew 安装（macOS）
brew install pnpm

# 使用 curl 安装
curl -fsSL https://get.pnpm.io/install.sh | sh -

# 查看版本
pnpm -v

# 查看 pnpm 配置
pnpm config list
```

## 三、常用命令对比

### 1. 初始化项目

```bash
# npm
npm init
npm init -y  # 使用默认配置

# Yarn
yarn init
yarn init -y

# pnpm
pnpm init
pnpm init -y
```

### 2. 安装依赖

```bash
# npm
npm install
npm i  # 简写

# Yarn
yarn install
yarn  # 简写

# pnpm
pnpm install
pnpm i  # 简写
```

### 3. 安装生产依赖

```bash
# npm
npm install react
npm install react@latest
npm install react@18.2.0

# Yarn
yarn add react
yarn add react@latest
yarn add react@18.2.0

# pnpm
pnpm add react
pnpm add react@latest
pnpm add react@18.2.0
```

### 4. 安装开发依赖

```bash
# npm
npm install --save-dev typescript
npm install -D typescript  # 简写

# Yarn
yarn add --dev typescript
yarn add -D typescript  # 简写

# pnpm
pnpm add --save-dev typescript
pnpm add -D typescript  # 简写
```

### 5. 全局安装

```bash
# npm
npm install --global create-react-app
npm install -g create-react-app  # 简写

# Yarn
yarn global add create-react-app

# pnpm
pnpm add --global create-react-app
pnpm add -g create-react-app  # 简写
```

### 6. 卸载依赖

```bash
# npm
npm uninstall react
npm un react  # 简写

# Yarn
yarn remove react

# pnpm
pnpm remove react
pnpm rm react  # 简写
```

### 7. 更新依赖

```bash
# npm
npm update
npm outdated  # 查看过期依赖

# Yarn
yarn upgrade
yarn outdated  # 查看过期依赖

# pnpm
pnpm update
pnpm outdated  # 查看过期依赖
```

### 8. 运行脚本

```bash
# package.json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest"
  }
}

# npm
npm run dev
npm run build
npm run test

# Yarn
yarn dev
yarn build
yarn test

# pnpm
pnpm dev
pnpm build
pnpm test
```

### 9. 清除缓存

```bash
# npm
npm cache clean --force

# Yarn
yarn cache clean

# pnpm
pnpm store prune
```

## 四、依赖管理对比

### 1. 依赖解析

#### npm

```bash
# npm 使用 package-lock.json
npm install

# 查看依赖树
npm ls
npm ls react
```

#### Yarn

```bash
# Yarn 使用 yarn.lock
yarn install

# 查看依赖树
yarn list
yarn list react
```

#### pnpm

```bash
# pnpm 使用 pnpm-lock.yaml
pnpm install

# 查看依赖树
pnpm list
pnpm list react
```

### 2. 依赖结构

#### npm（平铺结构）

```
node_modules/
  react/
  react-dom/
  lodash/
  ...
```

#### Yarn（平铺结构）

```
node_modules/
  react/
  react-dom/
  lodash/
  ...
```

#### pnpm（严格的嵌套结构）

```
node_modules/
  .pnpm/
    react@18.2.0/
      node_modules/
        react/
    react-dom@18.2.0/
      node_modules/
        react-dom/
  react -> .pnpm/react@18.2.0/node_modules/react
  react-dom -> .pnpm/react-dom@18.2.0/node_modules/react-dom
```

### 3. workspace 支持

#### npm

```json
{
  "name": "my-workspace",
  "private": true,
  "workspaces": [
    "packages/*"
  ]
}
```

```bash
# npm workspace
npm install
npm run build --workspace=packages/ui
npm run dev --workspaces
```

#### Yarn

```json
{
  "name": "my-workspace",
  "private": true,
  "workspaces": [
    "packages/*"
  ]
}
```

```bash
# Yarn workspace
yarn install
yarn workspace packages/ui build
yarn workspaces run dev
```

#### pnpm

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
```

```bash
# pnpm workspace
pnpm install
pnpm --filter packages/ui build
pnpm -r dev
```

## 五、性能对比

### 1. 安装速度

| 操作 | npm | Yarn | pnpm |
|------|-----|------|------|
| 首次安装 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 重复安装 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 缓存安装 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 2. 磁盘空间占用

| 项目数 | npm | Yarn | pnpm |
|--------|-----|------|------|
| 1 个项目 | 500MB | 500MB | 200MB |
| 5 个项目 | 2.5GB | 2.5GB | 300MB |
| 10 个项目 | 5GB | 5GB | 400MB |

pnpm 通过硬链接和符号链接，大大节省了磁盘空间。

## 六、配置文件对比

### 1. npm 配置

```bash
# npmrc 文件
npm config set registry https://registry.npmmirror.com
npm config set save-exact true
```

```ini
# .npmrc
registry=https://registry.npmmirror.com
save-exact=true
```

### 2. Yarn 配置

```bash
# yarnrc 文件
yarn config set registry https://registry.npmmirror.com
yarn config set save-exact true
```

```yaml
# .yarnrc
registry "https://registry.npmmirror.com"
save-exact true
```

### 3. pnpm 配置

```bash
# pnpmrc 文件
pnpm config set registry https://registry.npmmirror.com
pnpm config set save-exact true
```

```ini
# .npmrc
registry=https://registry.npmmirror.com
save-exact=true
shamefully-hoist=false
strict-peer-dependencies=true
```

## 七、实战指南

### 1. 选择合适的包管理器

#### 选择 npm 的情况

- 简单的个人项目
- 需要最广泛的生态支持
- 不想安装额外工具

```bash
# 使用 npm
npm init -y
npm install react react-dom
```

#### 选择 Yarn 的情况

- 需要更好的确定性
- 需要离线模式
- 项目中有大量依赖

```bash
# 使用 Yarn
yarn init -y
yarn add react react-dom
```

#### 选择 pnpm 的情况

- 追求极致的安装速度
- 有大量项目需要节省磁盘空间
- 需要严格的依赖管理

```bash
# 使用 pnpm
pnpm init -y
pnpm add react react-dom
```

### 2. 迁移指南

#### 从 npm 迁移到 pnpm

```bash
# 1. 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 2. 使用 pnpm 安装
pnpm install

# 3. 更新脚本（可选）
# package.json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
```

#### 从 Yarn 迁移到 pnpm

```bash
# 1. 删除 node_modules 和 yarn.lock
rm -rf node_modules yarn.lock

# 2. 使用 pnpm 安装
pnpm install
```

### 3. 混合使用注意事项

**不要在同一个项目中混合使用不同的包管理器！**

```bash
# ❌ 错误做法
npm install
yarn add react
pnpm update

# ✅ 正确做法
# 只使用一种包管理器
pnpm install
pnpm add react
pnpm update
```

## 八、高级功能

### 1. pnpm 的独特功能

#### 1.1 严格的 peer dependency 检查

```ini
# .npmrc
strict-peer-dependencies=true
```

#### 1.2 选择性 Hoisting

```ini
# .npmrc
shamefully-hoist=false
```

#### 1.3 Workspace 协议

```json
{
  "dependencies": {
    "shared-ui": "workspace:*"
  }
}
```

### 2. Yarn 的独特功能

#### 2.1 Yarn Berry（Yarn 2+）

```bash
# 安装 Yarn Berry
yarn set version berry

# 使用 Zero-Installs
yarn install
```

#### 2.2 Plug'n'Play

```yaml
# .yarnrc.yml
nodeLinker: pnp
```

### 3. npm 的独特功能

#### 3.1 npm audit

```bash
# 安全审计
npm audit
npm audit fix
npm audit fix --force
```

#### 3.2 npm fund

```bash
# 查看依赖的资金支持
npm fund
```

## 九、最佳实践

### 1. 项目初始化

```bash
# 使用 pnpm（推荐）
pnpm create vite my-project -- --template react-ts
cd my-project
pnpm install
```

### 2. 配置文件

```ini
# .npmrc
registry=https://registry.npmmirror.com
save-exact=true
auto-install-peers=true
```

### 3. 版本锁定

```json
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0",
    "pnpm": ">=8.0.0"
  },
  "packageManager": "pnpm@8.15.0"
}
```

### 4. CI/CD 配置

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8
          
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
          
      - name: Install dependencies
        run: pnpm install
        
      - name: Build
        run: pnpm build
```

## 十、总结

| 特性 | npm | Yarn | pnpm |
|------|-----|------|------|
| 安装速度 | 中 | 快 | 极快 |
| 磁盘占用 | 高 | 高 | 低 |
| 生态支持 | 最好 | 好 | 好 |
| 学习曲线 | 低 | 低 | 中 |
| 确定性 | 中 | 高 | 高 |
| 推荐指数 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**推荐选择：**

- **新项目**：推荐使用 pnpm，享受最快的速度和最低的磁盘占用
- **现有项目**：如果已经使用 npm 或 Yarn，可以继续使用，无需强制迁移
- **大型 monorepo**：强烈推荐 pnpm，workspace 支持非常优秀

选择适合自己项目的包管理器，才是最好的选择！

## 参考资料

- [npm 官方文档](https://docs.npmjs.com/)
- [Yarn 官方文档](https://yarnpkg.com/)
- [pnpm 官方文档](https://pnpm.io/)
- [Node.js 官方网站](https://nodejs.org/)
