# Zustand 与 Jotai 完全指南：React 轻量级状态管理

> 深入讲解 React 轻量级状态管理方案，包括 Zustand 和 Jotai 的使用，原子化状态设计，以及与 Redux/Context 的对比。

## 一、Zustand

### 1.1 安装

```bash
npm install zustand
```

### 1.2 创建 Store

```javascript
import { create } from 'zustand';

const useStore = create(set => ({
  count: 0,
  user: null,
  increment: () => set(state => ({ count: state.count + 1 })),
  setUser: (user) => set({ user })
}));
```

### 1.3 使用

```javascript
import useStore from './store';

function Counter() {
  const count = useStore(state => state.count);
  const increment = useStore(state => state.increment);
  
  return (
    <button onClick={increment}>
      {count}
    </button>
  );
}
```

## 二、Jotai

### 2.1 原子状态

```javascript
import { atom } from 'jotai';

const countAtom = atom(0);
const userAtom = atom(null);
```

### 2.2 派生状态

```javascript
const doubledAtom = atom(get => get(countAtom) * 2);

const userNameAtom = atom(
  get => get(userAtom)?.name || 'Guest'
);
```

### 2.3 使用

```javascript
import { useAtom } from 'jotai';

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  
  return (
    <button onClick={() => setCount(c => c + 1)}>
      {count}
    </button>
  );
}
```

## 三、对比

### 3.1 方案对比

| 方案 | 特点 |
|------|------|
| Zustand | 极简 API，Hook 风格 |
| Jotai | 原子化，天然支持派生 |
| Redux | 完整生态，调试工具 |
| Context | 内置，简单场景 |

### 3.2 选择建议

- 简单状态 → Zustand
- 复杂派生 → Jotai
- 大型项目 → Redux
- 极简需求 → Context

## 四、总结

React 状态管理核心要点：

1. **Zustand**：Hook 风格，极简
2. **Jotai**：原子化，派生简单
3. **atom**：状态原子
4. **getter**：派生计算
5. **useAtom**：使用状态

掌握这些，React 状态管理更简单！

---

**推荐阅读**：
- [Zustand 文档](https://zustand-demo.pmnd.rs/)
- [Jotai 文档](https://jotai.org/)

**如果对你有帮助，欢迎点赞收藏！**
