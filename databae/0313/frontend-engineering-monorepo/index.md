# 现代前端工程化链路：从 Monorepo、规范化到 CI/CD 的落地实践

> Monorepo（pnpm workspace）、ESLint/Prettier/提交规范、类型检查、单测与 E2E、GitHub Actions 发布与部署。

---

## 一、为什么需要工程化

前端项目一旦从「单页 Demo」变成「多包、多应用、多人协作」，就会遇到：**依赖版本不统一**、**代码风格各写各的**、**提交信息乱**、**上线靠人点**。工程化要解决的就是：用**约定 + 工具**把「怎么开发、怎么提交流程、怎么构建发布」固定下来，减少沟通成本和线上事故。

## 二、Monorepo：多包放在一个仓库

**Monorepo** 指一个仓库里放多个包/应用，通过 **workspace** 在根目录统一装依赖、统一跑脚本。好处是：依赖可提升、改库和改业务代码同仓、重构和版本一致性好控制。

### 2.1 pnpm workspace

用 **pnpm** 的 workspace 很常见：根目录有 `pnpm-workspace.yaml`，列出子包路径，例如：

```yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

根目录 `pnpm i` 会按 workspace 解析：子包之间用 `workspace:*` 引用，只会装一份，且连接在 `node_modules` 里。比 npm/yarn 的 hoist 更可控，磁盘也省。

### 2.2 子包结构示例

- `packages/ui`：组件库
- `packages/utils`：公共工具
- `apps/web`：主应用，依赖 `@repo/ui`、`@repo/utils`

每个子包有自己的 `package.json`（name、version、main/exports），根目录可以统一用 **Turbo** 或 **Nx** 做任务编排（build、test、lint 按依赖顺序或并行跑）。

## 三、代码规范：ESLint + Prettier

- **ESLint**：管逻辑/风格规则（如未使用变量、必须 return、React hooks 依赖）。
- **Prettier**：管格式（缩进、引号、分号）。两者配合时，一般 ESLint 关掉和格式冲突的规则，用 `eslint-config-prettier`，再在提交前或保存时跑 Prettier。

根目录一份 `.eslintrc`、`.prettierrc`，子包可继承或覆盖。这样全仓风格一致，CR 时少扯皮。

## 四、提交规范：Commitlint + Husky

- **Commitlint**：校验 commit message 格式，常见约定是 `type(scope): subject`，如 `feat(web): 增加登录页`。类型可以是 feat、fix、docs、chore 等。
- **Husky**：在 git hooks 里挂脚本，例如 `pre-commit` 跑 lint-staged（只对暂存文件做 lint/format），`commit-msg` 跑 commitlint。这样不合格的提交会被拦在本地。

配合 **standard-version** 或 **changesets** 可以按约定自动升版本、生成 CHANGELOG。

## 五、类型检查与构建

- **TypeScript**：根目录或各子包有 `tsconfig.json`，通过 `references` 做项目引用，保证类型在包边界也正确。
- **构建**：各子包用 Vite/Rollup/tsup 等打出 ESM/CJS 和类型声明，主应用再引用这些产物。Monorepo 里通常「先 build 被依赖的包，再 build 应用」。

## 六、测试：单测与 E2E

- **单测**：Vitest/Jest，对工具函数、组件（配合 Testing Library）做单元测试，在 CI 里必过才让合并。
- **E2E**：Playwright/Cypress，对关键流程做端到端，可在 PR 或 nightly 跑。和单测一起构成「质量门禁」。

## 七、CI/CD：GitHub Actions 示例

在 `.github/workflows` 里写 YAML：**on push/PR** 触发，拉代码、装依赖（pnpm）、跑 lint、类型检查、单测、构建；通过后再部署（如发到 OSS、或触发内部发布平台）。示例片段：

```yaml
- run: pnpm i -r
- run: pnpm run lint
- run: pnpm run typecheck
- run: pnpm run test
- run: pnpm run build
```

部署步骤可按环境用不同 secret（如 OSS 的 key）、不同分支（main 上生产，dev 上预览）。

## 八、小结

现代前端工程化 = **Monorepo（pnpm workspace）+ 规范（ESLint/Prettier/Commitlint/Husky）+ 类型与构建 + 单测/E2E + CI/CD**。从「能跑」到「能稳、能协作、能发布」，把上面每一块按项目规模选配好，就能形成可复用的工程底座。

## 九、目录结构示例

```
repo/
├── pnpm-workspace.yaml
├── package.json
├── .eslintrc.cjs
├── .prettierrc
├── packages/
│   ├── ui/          # 组件库
│   ├── utils/       # 工具函数
│   └── types/       # 共享类型
└── apps/
    ├── web/         # 主应用
    └── admin/       # 后台
```

根 `package.json` 里 scripts 可写 `"build": "pnpm -r run build"` 或交给 Turbo/Nx 按图执行。

## 十、规范落地检查清单

- [ ] 新 MR 必须通过 lint、typecheck、test
- [ ] commit message 符合 Commitlint 约定
- [ ] 主分支保护：禁止 force push，必须通过 CI
- [ ] 发布流程：打 tag 或合并 main 触发 build + 部署，版本与 CHANGELOG 自动更新

把这些做成团队共识和流水线硬约束，工程化才算真正落地。

## 十一、依赖升级与安全

Monorepo 里依赖多，建议用 **pnpm audit**、**npm audit** 或 Dependabot 做漏洞扫描；升级时用 `pnpm update -r` 按 workspace 批量升，再跑一遍 test 和 build。大版本升级（如 React 17→18）可以先在一个子包或分支试跑，再推广到全仓。依赖锁文件（pnpm-lock.yaml）务必提交，CI 里用 `pnpm i --frozen-lockfile` 保证环境一致。

## 十二、文档与 Onboarding

工程化不只管代码，还要管「新人怎么上手」。在根目录维护一份 README：如何装依赖、如何跑 dev/build、目录约定、提交流程、发布流程。有变更及时更新。必要时用 **Changeset** 或 **Lerna** 的 version 流程写清楚「这次发布改了哪些包、是否破坏性」，减少协作成本。
