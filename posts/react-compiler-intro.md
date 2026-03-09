# React Compiler 来了：少写 useMemo，照样稳

> 编译期自动分析依赖、帮你做 memoization，从此不用再纠结「这段要不要包 useMemo」——用愉悦分享的语气，带你认识 React 官方的这份新礼物。

---

## 一、先说说我们都在纠结啥

写 React 的时候，咱们多少都经历过这种灵魂拷问：**这个算出来的值要不要包一层 useMemo？这个回调要不要 useCallback？这个子组件要不要 React.memo？** 不包怕重渲染，包多了又觉得代码啰嗦，还容易依赖数组写错。

有没有一种可能——**我们只管写逻辑，谁来帮我们自动做「该记的记一下」？** 有，这就是 **React Compiler** 想做的事。

---

## 二、React Compiler 是什么

**React Compiler**（以前叫 React Forget）是 React 官方出的一个 **编译期插件**：在构建时分析你的组件代码，搞清楚「谁依赖谁」，然后在需要的地方**自动**插入 memoization，相当于帮你自动加 useMemo / useCallback / React.memo，而不是你自己一个个手写。

- **是什么**：Babel 插件（或与 Vite / Next 等集成），跑在构建阶段。
- **解决啥**：减少手写 useMemo/useCallback/React.memo 的心智负担，同时尽量保持「只在该变的时候重算、重渲染」。
- **和手写区别**：你写的是「普通」React 代码，编译器在背后做优化；依赖分析由工具完成，更一致、也少踩依赖数组的坑。

一句话：**写得更爽，性能交给编译器。**

---

## 三、它有什么用、适合谁

- **典型场景**：中大型列表、表单、多状态联动组件，以前你要反复想「这里要不要 memo」的地方，可以优先交给编译器试一试。
- **适用人群**：用 React 17/18/19 的团队，尤其是已经在用 Vite、Next.js、Babel 的；想统一优化策略、减少 useMemo 样板代码的。
- **你能得到**：更少的样板代码、更少的依赖数组 bug、以及（在编译器覆盖到的路径上）更可预期的重渲染行为。注意：它**不会**取代所有手写优化，但在很多场景下能覆盖大部分需求。

---

## 四、官方链接（方便你溯源）

- **React 官方介绍**：[React Compiler – React](https://react.dev/learn/react-compiler)
- **配置说明**：[Configuration – React](https://react.dev/reference/react-compiler/configuration)
- **安装步骤**：[Installation – React](https://react.dev/learn/react-compiler/installation)
- **Babel 插件**：`babel-plugin-react-compiler`（npm 上搜即可）

建议先看官方 Learn 里的介绍，再看 Installation，按你的构建工具选一条路即可。

---

## 五、从零跑起来（以 Vite + React 为例）

### 环境要求

- Node 18+
- React 17 / 18 / 19 均可（React 19 体验最佳）
- 已有 Vite + React 项目（或 `npm create vite@latest` 选 React）

### 安装

```bash
pnpm add -D babel-plugin-react-compiler
# 若 React 版本 < 19，再装运行时
pnpm add react-compiler-runtime
```

### Vite 里怎么开

用 `@vitejs/plugin-react` 时，在 `vite.config.ts` 里打开 compiler 开关即可：

```javascript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [
        react({
            babel: {
                plugins: [['babel-plugin-react-compiler', {}]],
            },
        }),
    ],
});
```

保存后重新跑 `pnpm dev`，编译器就会参与构建。**注意**：Babel 里若有其他插件，官方建议把 React Compiler 放在**第一个**，这样它能拿到更完整的源码信息做分析。

### 用 Next.js 的话

Next.js 15+ 已内置支持，在 `next.config.js` 里开：

```javascript
// next.config.js
const nextConfig = {
    experimental: {
        reactCompiler: true,
    },
};
```

---

## 六、写一小段「不写 useMemo」的代码试试

下面是一段**没写任何 useMemo / useCallback** 的组件——在开启 React Compiler 后，编译器会在编译期分析依赖，并在需要时自动做 memoization，你可以对比开启前后的重渲染行为（例如用 React DevTools 的 Profiler）。

```jsx
function TodoList({ todos, onToggle }) {
    const [filter, setFilter] = useState('all');
    const filtered = todos.filter((t) =>
        filter === 'done' ? t.done : filter === 'pending' ? !t.done : true
    );
    return (
        <div>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                <option value="all">全部</option>
                <option value="done">已完成</option>
                <option value="pending">未完成</option>
            </select>
            <ul>
                {filtered.map((t) => (
                    <li key={t.id} onClick={() => onToggle(t.id)}>
                        {t.title}
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

以前我们可能会给 `filtered` 包一层 useMemo、给 `onToggle` 包 useCallback；**在开启 React Compiler 之后**，这类简单依赖可以交给编译器处理，你先专注把逻辑写清楚就行。

---

## 七、一点注意与小结

- **兼容性**：推荐 React 19；若用 17/18，需安装 `react-compiler-runtime` 并按官方文档配置。
- **渐进使用**：可以先在部分页面或分支开启，观察构建与运行是否稳定，再逐步铺开。
- **不是银弹**：极端性能敏感、或已有精细手写 memo 的地方，可以保留；编译器是「默认帮你省心」，而不是禁止你手写。

**小结几句**：React Compiler 用「编译期分析依赖 + 自动 memoization」的方式，让我们少写 useMemo/useCallback/React.memo，代码更干净、心智负担更小。如果你一直在纠结「这段要不要包 useMemo」，不妨在项目里开一次 React Compiler，用愉悦的心态试一把——说不定你会喜欢上这种「写逻辑、优化交给编译器」的感觉。

如果这篇对你有帮助，欢迎点赞 / 收藏；你有在项目里用过 React Compiler 吗？欢迎在评论区聊聊你的体验。

---

**标签建议**：`React`、`前端`、`性能优化`、`Vite`、`React Compiler`
