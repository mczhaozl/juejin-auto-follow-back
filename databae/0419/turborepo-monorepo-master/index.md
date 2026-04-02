# Turborepo 完全指南：现代化 Monorepo 管理利器

> 一句话摘要：深入解析 Turborepo 的核心概念、缓存机制、任务调度和最佳实践，学习如何用它管理大型前端 monorepo 项目，提升开发体验和构建性能。

## 一、Monorepo 概述

### 1.1 什么是 Monorepo

Monorepo（单体仓库）是一种将多个项目放在同一个代码仓库中的开发策略：

```
┌─────────────────────────────────────────────────────────┐
│                    Monorepo 仓库                         │
├─────────────────────────────────────────────────────────┤
│  packages/                                              │
│    ├── ui/           ← 共享 UI 组件库                    │
│    ├── utils/        ← 共享工具函数                      │
│    ├── config/       ← 共享配置                         │
│    └── ...                                               │
│  apps/                                                  │
│    ├── web/          ← 主 Web 应用                       │
│    ├── docs/         ← 文档站点                          │
│    ├── admin/        ← 管理后台                          │
│    └── mobile/       ← 移动端应用                        │
│  services/                                              │
│    ├── api/          ← 后端 API 服务                     │
│    └── cron/         ← 定时任务服务                      │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Monorepo 的优势

| 优势 | 说明 |
|------|------|
| 代码共享 | 轻松共享组件、工具、类型定义 |
| 原子提交 | 一次提交修改多个相关包 |
| 统一工具链 | ESLint、Prettier、TypeScript 配置统一 |
| 依赖管理 | 共享 node_modules，避免重复安装 |
| 协作简化 | 跨项目改动更容易 review 和管理 |

### 1.3 Monorepo 的挑战

| 挑战 | 传统工具痛点 |
|------|-------------|
| 构建性能 | 改动一个包，全量重新构建 |
| 依赖复杂 | 包之间的依赖关系难以管理 |
| 测试困难 | 不知道哪些包需要重新测试 |
| CI 慢 | 每次都构建所有项目 |

**Turborepo 正是为了解决这些问题而生的。**

## 二、Turborepo 核心概念

### 2.1 什么是 Turborepo

Turborepo 是 Vercel 开发的 monorepo 构建工具，核心特性：

- **智能缓存**：基于任务输入的哈希缓存
- **增量构建**：只重新构建受影响的包
- **并行执行**：最大化利用多核 CPU
- **任务协调**：定义包之间的构建顺序

```
┌─────────────────────────────────────────────────┐
│                 Turborepo 工作流程                │
├─────────────────────────────────────────────────┤
│                                                  │
│   代码变更 ──→ 任务图分析 ──→ 缓存查找 ──→ 执行    │
│                  ↓                ↓               │
│            依赖拓扑排序    命中缓存？跳过构建       │
│                  ↓               ↓                │
│            并行调度任务    未命中？执行并缓存       │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 2.2 关键术语

| 术语 | 说明 |
|------|------|
| Workspace | 工作区，对应一个包 |
| Task | 任务，如 build、test、lint |
| Pipeline | 任务管道，定义任务依赖关系 |
| Cache | 缓存，基于输入的哈希 |
| Remote Cache | 远程缓存，团队共享 |
| Ghost Mode | 幽灵模式，不生成输出文件 |

### 2.3 快速开始

```bash
# 创建新的 monorepo
npx create-turbo@latest my-monorepo

# 或在现有项目添加 Turborepo
npm install -D turbo

# 初始化
npx turbo init
```

### 2.4 目录结构

```
my-monorepo/
├── apps/
│   └── web/
│       ├── package.json
│       ├── turbo.json
│       └── ... (项目文件)
├── packages/
│   └── ui/
│       ├── package.json
│       ├── turbo.json
│       └── ... (组件库文件)
├── package.json        ← 根 package.json
├── turbo.json          ← 根 turbo.json
└── pnpm-workspace.yaml ← pnpm 工作区配置
```

## 三、turbo.json 配置详解

### 3.1 基础配置

```json
// turbo.json
{
    "$schema": "https://turbo.build/schema.json",
    "globalDependencies": [
        ".env"
    ],
    "pipeline": {
        "build": {
            "dependsOn": ["^build"],
            "outputs": ["dist/**", ".next/**"]
        },
        "test": {
            "dependsOn": ["build"],
            "outputs": ["coverage/**"]
        },
        "lint": {
            "outputs": []
        },
        "dev": {
            "cache": false,
            "persistent": true
        }
    }
}
```

### 3.2 任务依赖（dependsOn）

```json
{
    "pipeline": {
        "build": {
            // ^build 表示"依赖于所有依赖包的 build 任务"
            "dependsOn": ["^build"],
            "outputs": ["dist/**"]
        },
        "test": {
            // 只依赖于当前包的 build
            "dependsOn": ["build"],
            "outputs": ["coverage/**"]
        },
        "lint": {
            // 无依赖
            "dependsOn": []
        }
    }
}
```

### 3.3 任务排序

```json
{
    "pipeline": {
        "//#build": {
            // 根包的构建任务，无前辈
        },
        "build": {
            "dependsOn": ["^build"],
            // 这意味着：
            // 1. 先构建所有依赖包
            // 2. 再构建当前包
        },
        "test": {
            "dependsOn": ["build"],
            // 这意味着：
            // 1. 先构建当前包
            // 2. 再运行测试
        }
    }
}
```

### 3.4 输出配置

```json
{
    "pipeline": {
        "build": {
            "dependsOn": ["^build"],
            // 指定哪些文件/目录是输出
            // 这些会被缓存
            "outputs": [
                "dist/**",
                ".next/**",
                "!.next/cache/**"
            ]
        },
        "test": {
            "outputs": ["coverage/**"]
        },
        "lint": {
            // 空数组表示无输出，不缓存
            "outputs": []
        },
        "dev": {
            // dev 任务默认不缓存（因为是持续运行的）
            "cache": false,
            "persistent": true
        }
    }
}
```

### 3.5 环境变量

```json
{
    "globalDependencies": [
        ".env",
        ".env.local"
    ],
    "pipeline": {
        "build": {
            "dependsOn": ["^build"],
            "env": [
                "NODE_ENV",
                "API_URL"
            ],
            "outputs": ["dist/**"]
        }
    }
}
```

## 四、缓存机制深度解析

### 4.1 缓存原理

Turborepo 使用 **Content Hash** 来判断是否需要重新执行任务：

```
┌─────────────────────────────────────────────────────────┐
│                    缓存命中判断                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   输入文件 Hash ──┬──→ Hash 合并 ──→ 任务 Hash           │
│                   │                                       │
│   环境变量 Hash ──┘        ↓                              │
│                        缓存查询 ──→ 命中？──→ 恢复输出    │
│                                          ↓               │
│                                         未命中 ──→ 执行  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.2 本地缓存

```bash
# 查看本地缓存
turbo cache

# 删除本地缓存
turbo cache delete

# 查看缓存目录
ls ~/.cache/turbo

# 指定缓存目录
turbo build --cache-dir ./node_modules/.cache/turbo
```

### 4.3 远程缓存

```bash
# 登录 Vercel（远程缓存服务）
npx turbo login

# 链接项目
npx turbo link

# 启用远程缓存后，CI 也可共享缓存
```

### 4.4 自定义远程缓存

```typescript
// turbo-repo-custom-cache.ts
import type { TurboTasksCache } from '@turbo/cache';

class CustomCache implements TurboTasksCache {
    async get(key: string): Promise<Cache Miss | CacheEntry> {
        // 从远程存储获取
        const data = await remoteStorage.get(key);
        if (data) {
            return {
                files: data.files,
                duration: data.duration
            };
        }
        return CacheMiss;
    }

    async set(
        key: string,
        files: string[],
        meta: { duration?: number; }
    ): Promise<void> {
        // 上传到远程存储
        await remoteStorage.put(key, {
            files,
            duration: meta.duration
        });
    }
}
```

### 4.5 缓存调试

```bash
# 查看任务执行的详细信息
turbo build --verbosity=2

# 强制忽略缓存
turbo build --force

# 查看缓存状态
turbo build --dry-run=json

# 只输出哈希，不执行
turbo build --dry-run
```

## 五、任务执行详解

### 5.1 任务图构建

```bash
# 可视化任务依赖图
turbo graph

# 生成 PNG 图片
turbo graph --type="png"
```

### 5.2 并行执行

```bash
# 最大并行任务数（默认 CPU 核心数）
turbo build --parallel

# 限制最大并行数
turbo build --jobs=4
```

### 5.3 过滤（Filtering）

```bash
# 只构建特定包
turbo build --filter=@repo/web

# 排除特定包
turbo build --filter=!@repo/docs

# 构建包及其依赖
turbo build --filter=@repo/web...

# 构建包及其被依赖者（影响分析）
turbo build --filter=...@repo/web
```

### 5.4 影响分析

```bash
# 检测哪些包受到了影响
turbo build --filter=...[HEAD~1]

# 对比两个分支的差异
turbo build --filter=...[origin/main]
```

### 5.5 完整示例

```bash
# 只构建受当前改动影响的包
git diff HEAD~1 --name-only | \
  xargs -I{} dirname {} | \
  sort -u | \
  xargs -I{} basename {} | \
  xargs -I{} turbo build --filter={}
```

## 六、实战配置

### 6.1 Next.js 应用

```json
// apps/web/turbo.json
{
    "extends": ["//#build"],
    "pipeline": {
        "build": {
            "outputs": [".next/**", "!.next/cache/**"]
        },
        "dev": {
            "cache": false,
            "persistent": true
        }
    }
}
```

### 6.2 React 组件库

```json
// packages/ui/turbo.json
{
    "extends": ["//#build"],
    "pipeline": {
        "build": {
            "outputs": ["dist/**"],
            "env": ["NODE_ENV"]
        },
        "lint": {
            "outputs": []
        },
        "test": {
            "dependsOn": ["build"],
            "outputs": ["coverage/**"]
        }
    }
}
```

### 6.3 工具包

```json
// packages/utils/turbo.json
{
    "extends": ["//#build"],
    "pipeline": {
        "build": {
            "outputs": ["dist/**"]
        },
        "test": {
            "dependsOn": ["build"],
            "outputs": ["coverage/**"]
        }
    }
}
```

### 6.4 统一的任务管道

```json
// turbo.json (根目录)
{
    "$schema": "https://turbo.build/schema.json",
    "globalDependencies": [".env"],
    "pipeline": {
        "build": {
            "dependsOn": ["^build"],
            "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
            "env": ["NODE_ENV"]
        },
        "dev": {
            "cache": false,
            "persistent": true
        },
        "lint": {
            "outputs": []
        },
        "test": {
            "dependsOn": ["build"],
            "outputs": ["coverage/**"],
            "inputs": ["src/**/*.tsx", "src/**/*.ts", "test/**/*.ts"]
        },
        "typecheck": {
            "dependsOn": ["^build"],
            "outputs": []
        },
        "clean": {
            "cache": false
        }
    }
}
```

## 七、与 npm/pnpm/yarn workspace 集成

### 7.1 pnpm 配置

```yaml
# pnpm-workspace.yaml
packages:
    - 'apps/*'
    - 'packages/*'
```

```toml
# .npmrc
shamefully-hoist=true
```

### 7.2 依赖链接

```
# Turborepo + pnpm 的依赖结构
node_modules/
├── .pnpm/
│   ├── react@18.2.0/
│   └── react-dom@18.2.0/
└── .cache/
    └── turbo/  ← Turborepo 缓存
```

### 7.3 跨包引用

```json
// packages/ui/package.json
{
    "name": "@repo/ui",
    "exports": {
        ".": "./src/index.ts",
        "./button": "./src/button/index.ts",
        "./input": "./src/input/index.ts"
    }
}

// apps/web/package.json
{
    "dependencies": {
        "@repo/ui": "workspace:*"
    }
}
```

## 八、最佳实践

### 8.1 任务设计原则

```json
{
    "pipeline": {
        "build": {
            "dependsOn": ["^build"],
            "outputs": ["dist/**"]
        },
        "test": {
            "dependsOn": ["build"],
            "outputs": ["coverage/**"]
        },
        "lint": {
            "outputs": []
        },
        "typecheck": {
            "outputs": []
        }
    }
}
```

### 8.2 构建顺序

```
build 任务执行顺序：

1. 分析包依赖图
   @repo/utils
       ↓
   @repo/ui (依赖 @repo/utils)
       ↓
   @repo/web (依赖 @repo/ui, @repo/utils)

2. 按拓扑排序并行执行：
   - 第一波：@repo/utils
   - 第二波：@repo/ui (等待 utils 完成)
   - 第三波：@repo/web (等待 ui 完成)
```

### 8.3 环境变量管理

```typescript
// packages/shared-utils/src/config.ts
export const config = {
    apiUrl: process.env.API_URL || 'http://localhost:3000',
    env: process.env.NODE_ENV
};
```

### 8.4 共享配置

```json
// packages/eslint-config/index.js
module.exports = {
    extends: ['next', 'turbo'],
    rules: {
        // 自定义规则
    }
};
```

## 九、CI/CD 集成

### 9.1 GitHub Actions

```yaml
# .github/workflows/ci.yml
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
              run: turbo build

            - name: Test
              run: turbo test

            - name: Lint
              run: turbo lint
```

### 9.2 GitHub Actions 与远程缓存

```yaml
# .github/workflows/ci.yml
jobs:
    build:
        steps:
            - uses: actions/checkout@v4

            - name: Setup Node.js
              uses: actions/setup-node@v4
              with:
                  node-version: 20
                  cache: 'pnpm'

            - name: Setup Turborepo
              run: pnpm install turbo --global

            - name: Login to Vercel
              run: turbo login --token ${{ secrets.TURBO_TOKEN }}

            - name: Build
              run: turbo build --filter=...[HEAD~1]
              env:
                  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
                  TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

### 9.3 GitLab CI

```yaml
# .gitlab-ci.yml
stages:
    - build
    - test

build:
    stage: build
    image: node:20
    script:
        - npm install -g pnpm
        - pnpm install
        - turbo build
    cache:
        key: turbo
        paths:
            - .npm
            - .cache/turbo

test:
    stage: test
    script:
        - turbo test
    dependencies:
        - build
```

## 十、性能优化

### 10.1 构建缓存优化

```json
{
    "pipeline": {
        "build": {
            "outputs": ["dist/**"],
            "inputs": [
                "src/**",
                "package.json",
                "tsconfig.json",
                "!src/**/*.test.ts"
            ]
        }
    }
}
```

### 10.2 并行度调整

```bash
# 增加并行度
turbo build --jobs=8

# 使用所有 CPU 核心（默认）
turbo build --jobs=-1
```

### 10.3 增量构建

```bash
# 启用增量构建（需要远程缓存）
turbo build --force

# 只构建受影响的包
turbo build --filter=...[HEAD~1]
```

## 十一、常见问题与解决方案

### 11.1 构建失败

```bash
# 清除缓存重新构建
turbo build --force

# 查看详细错误
turbo build --verbosity=2
```

### 11.2 包依赖循环

```bash
# 检测循环依赖
turbo build --detect-public-duplicates
```

### 11.3 缓存失效

```json
// 排除频繁变化的文件
{
    "pipeline": {
        "build": {
            "inputs": [
                "src/**",
                "package.json",
                "tsconfig.json",
                "!*.test.ts",
                "!*.test.tsx"
            ]
        }
    }
}
```

## 十二、总结

### 12.1 核心要点

1. **Turborepo 通过内容哈希实现智能缓存**
2. **任务管道（pipeline）定义构建顺序和依赖**
3. **基于依赖拓扑排序的并行执行**
4. **远程缓存实现团队共享构建结果**
5. **过滤器实现精准的部分构建**

### 12.2 使用建议

- ✅ 使用 pnpm workspace 获得最佳性能
- ✅ 配置合理的 outputs 和 inputs
- ✅ 在 CI 中启用远程缓存
- ✅ 使用 --filter 进行增量构建
- ❌ 不要在 outputs 中包含 node_modules
- ❌ 不要缓存 dev 任务

### 12.3 资源链接

- [Turborepo 官方文档](https://turbo.build/repo)
- [Vercel Remote Cache](https://vercel.com/docs/concepts/monorepos/turborepo)
- [Turborepo GitHub](https://github.com/vercel/turbo)

> 如果对你有帮助，欢迎点赞、收藏！有任何问题欢迎在评论区讨论。
