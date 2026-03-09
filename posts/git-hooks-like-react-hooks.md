# 像 React Hook 一样「自动触发」：用 Git Hook 拦住忘删的测试代码与其它翻车现场

> 每次 commit 前总忘记删 `console.log`、`debugger` 或测试里的 `.only`？用 Git Hook 在提交/推送时自动跑检查，像 React Hook 一样在「关键时刻」自动执行，再也不用靠记性。文中顺带覆盖误提交敏感信息、错误分支、大文件等常见场景的拦截方式。

---

## 一、痛点：忘删测试代码，还有哪些「总是忘」的坑

我们在开发时经常顺手打 `console.log`、下断点 `debugger`，或为了单测只跑一个用例而加上 `it.only` / `test.only`，提交时一不留神就带上了。等到 CI 红、Code Review 被点名，才想起来要删。**光靠「记得检查」不可靠**，最好在 **commit / push 那一刻自动跑一遍检查**。

除了「忘删测试代码」，还有不少类似场景：

- **忘跑 lint / 格式化**：本地改完直接 commit，没跑 ESLint、Prettier，把格式问题或明显错误推进仓库。
- **误提交敏感信息**：把 `.env`、密钥、内网地址提交上去，事后要清理历史、改密钥，成本高。
- **在错误分支上提交**：本想在 `feature/xxx` 上改，结果在 `main` 上 commit 了，推送前没发现。
- **提交了不该提交的大文件**：node_modules、构建产物、大资源被打包进仓库，推上去才发现。
- **commit message 太随意**：全是「fix」「update」之类，不利于回溯和规范协作。

这些都可以通过 **Git Hook** 在「提交前 / 推送前」自动执行脚本，**像 React Hook 在渲染/副作用时机自动执行一样**，在「关键动作」时自动跑检查，不依赖你记得。

---

## 二、Git Hook 是什么、为何能「自动」触发

**Git Hook** 是 Git 在特定事件（如 `commit`、`push`）发生时自动执行的脚本，放在仓库 `.git/hooks/` 下，例如：

- **pre-commit**：在 `git commit` 完成前执行，若脚本非 0 退出，提交会被中止。
- **commit-msg**：在写完 commit message 后执行，可校验 message 格式。
- **pre-push**：在 `git push` 完成前执行，适合跑测试、检查分支等。

**「像 React Hook 一样触发」** 指的是：你不用在每次提交前手动跑「删没删 console、跑没跑 lint」，只要执行 `git commit` 或 `git push`，对应 hook 就会自动跑；**关键动作即触发**，习惯成自然。

原生用法是往 `.git/hooks/` 里塞脚本，但该目录不会随仓库分发，团队每人要自己配。所以实践中常用 **Husky** 把 hook 定义到仓库里（例如 `.husky/pre-commit`），`npm install` 后自动装好，大家拉代码就有同一套「自动触发」规则。

---

## 三、实战：Husky + lint-staged，pre-commit 拦住测试代码与 lint

用 **Husky** 管理 hook，用 **lint-staged** 只对暂存区文件执行检查（快、只扫改动的），在 **pre-commit** 里做两件事：**检查是否带了测试代码残留**，以及 **跑 ESLint（可选 Prettier）**。

### 3.1 安装与初始化

```bash
pnpm add -D husky lint-staged
npx husky init
```

会在项目根目录生成 `.husky/`，并创建 `.husky/pre-commit`。把 pre-commit 的内容改成：先跑「测试代码检测」，再跑 lint-staged。

### 3.2 检测「忘删的测试代码」

可以用简单脚本或现成工具扫描暂存区里的文件，禁止出现 `console.log`、`debugger`、`it.only`、`test.only`、`describe.only` 等。下面用 Node 写一个最小示例，只检查暂存区（和 lint-staged 一致）：

```javascript
// scripts/check-no-debug.js（放在项目里，pre-commit 里调用）
const { execSync } = require('child_process');
const path = require('path');

const patterns = [
    { pattern: /console\.(log|debug|info|warn|error)\s*\(/, msg: 'console.log/debug 等' },
    { pattern: /\bdebugger\s*;?/, msg: 'debugger' },
    { pattern: /(it|test|describe)\.only\s*\(/, msg: 'it.only / test.only / describe.only' },
];

const files = execSync('git diff --cached --name-only --diff-filter=ACM')
    .toString()
    .trim()
    .split('\n')
    .filter((f) => /\.(js|jsx|ts|tsx|vue|mjs|cjs)$/.test(f));

const found = [];
for (const file of files) {
    if (!file) continue;
    const content = require('fs').readFileSync(path.join(process.cwd(), file), 'utf-8');
    for (const { pattern, msg } of patterns) {
        if (pattern.test(content)) found.push(`${file}: 疑似含 ${msg}`);
    }
}
if (found.length) {
    console.error('pre-commit 检查未通过，请移除调试/测试专用代码：\n' + found.join('\n'));
    process.exit(1);
}
```

pre-commit 里先执行：`node scripts/check-no-debug.js`，再执行 lint-staged。

### 3.3 配置 lint-staged

在 `package.json` 里配好 **lint-staged**，只对暂存区的指定类型文件跑 ESLint（和可选 Prettier）：

```json
{
    "lint-staged": {
        "*.{js,jsx,ts,tsx,vue}": ["eslint --fix"]
    }
}
```

若还要格式化，可加上 `prettier --write`。

### 3.4 pre-commit 最终长什么样

`.husky/pre-commit` 内容示例：

```sh
node scripts/check-no-debug.js
npx lint-staged
```

这样每次 `git commit` 时都会**自动**：先扫暂存区是否还有 console/debugger/.only，再对暂存文件跑 lint。像 React Hook 一样，在「提交」这个关键时刻自动执行，无需你记得。

---

## 四、其它场景：敏感信息、错误分支、大文件、commit message

在「自动触发」这一思路上，可以按需加更多 hook 或脚本。

| 场景           | 做法简述 |
|----------------|----------|
| **敏感信息**   | pre-commit 里用 `grep` 或脚本扫暂存区，匹配密钥、`.env`、内网 IP 等正则，命中则 exit 1；也可用现成工具如 `detect-secrets`。 |
| **错误分支**   | pre-push 或 pre-commit 里读 `git branch --show-current`，若当前是 `main`/`master` 且存在未合并改动，则提示或直接拒绝。 |
| **大文件**     | pre-commit 里用 `git diff --cached` 查暂存区新增文件大小，超过阈值（如 1MB）则拒绝；或配合 `git-lfs` 规范大文件。 |
| **commit message** | 在 **commit-msg** hook 里读 `$1`（message 文件），用正则或约定（如 Conventional Commits）校验，不符合则 exit 1。 |

这些脚本都可以放在仓库里（如 `scripts/`），在 `.husky/pre-commit`、`.husky/pre-push`、`.husky/commit-msg` 里调用，团队拉代码即享同一套「自动触发」规则。

---

## 五、总结与参考

- **像 React Hook 一样触发**：Git Hook 在 `commit` / `push` 等关键动作时**自动执行**，不依赖你记得删测试代码、跑 lint。
- **忘删测试代码**：用 Husky 的 **pre-commit** + 自写脚本（或类似逻辑）扫暂存区，禁止 `console.log`、`debugger`、`it.only` 等，再配合 **lint-staged** 跑 ESLint。
- **其它翻车场景**：敏感信息、错误分支、大文件、commit message 可在 pre-commit / pre-push / commit-msg 里加检查，统一放在仓库里用 Husky 管理，团队共享。

**参考**：

- [Husky](https://typicode.github.io/husky/)
- [lint-staged](https://github.com/okonet/lint-staged)
- [Git 文档 - Hooks](https://git-scm.com/docs/githooks)

把「记得检查」交给 Git Hook，你只管写代码、commit，剩下的让 hook 自动跑。若对你有用，欢迎点赞、收藏或评论区分享你的 hook 配置。
