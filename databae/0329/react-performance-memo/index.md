# React 性能优化：深度理解 useMemo 与 useCallback

> React 的渲染机制非常强大，但如果使用不当，很容易陷入「过度渲染」的泥潭。`useMemo` 和 `useCallback` 是 React 提供的两个核心优化钩子，但它们也是被误用最频繁的工具。本文将带你深入底层原理，理清它们的使用边界，帮你写出真正高性能的 React 代码。

---

## 一、React 的渲染逻辑：为什么会慢？

React 的默认行为是：**只要父组件渲染，子组件就会跟着渲染**。
- **Reconciliation**：React 会对比新旧虚拟 DOM 树。虽然 Diff 算法很快，但在大型组件树中，频繁的 Diff 依然会造成明显的掉帧。
- **引用相等性 (Referential Equality)**：在 JS 中，每次定义的函数或对象都是新的引用。这会导致即便数据没变，子组件也会因为 Props 引用变化而重绘。

---

## 二、useMemo：缓存计算结果

`useMemo` 用于缓存昂贵的计算结果。只有当依赖项发生变化时，才会重新计算。

### 2.1 使用场景
- **昂贵的 CPU 计算**：如大数组的排序、过滤、复杂的数学运算。
- **保持对象的引用稳定**：防止子组件因为对象 Prop 的引用变化而重新渲染。

### 代码示例：优化列表过滤
```javascript
const filteredList = useMemo(() => {
  console.log('正在执行昂贵的过滤操作...');
  return list.filter(item => item.value > threshold);
}, [list, threshold]);
```

---

## 三、useCallback：缓存函数引用

`useCallback` 的本质是 `useMemo(() => fn, deps)`。它返回的是函数的**引用**。

### 3.1 核心误区：并不是所有函数都要包裹它
包裹 `useCallback` 本身也有开销（定义依赖数组、闭包存储）。
- **正确场景**：当函数作为 Prop 传递给经过 `React.memo` 优化的子组件时。
- **无效场景**：直接在普通 HTML 标签（如 `<button>`）上使用的点击事件。

### 代码示例：配合 React.memo 使用
```javascript
const Child = React.memo(({ onClick }) => {
  console.log('子组件渲染');
  return <button onClick={onClick}>点击我</button>;
});

function Parent() {
  const [count, setCount] = useState(0);
  
  // 如果不使用 useCallback，Parent 每次渲染都会生成新函数，导致 Child 重新渲染
  const handleClick = useCallback(() => {
    console.log('点击了');
  }, []);

  return (
    <>
      <Child onClick={handleClick} />
      <button onClick={() => setCount(c => c + 1)}>父组件增加 {count}</button>
    </>
  );
}
```

---

## 四、优化陷阱：不要过度优化

1. **依赖项数组的陷阱**：如果依赖项漏写，会导致闭包过时（Stale Closure）；如果依赖项写得太多，优化就失去了意义。
2. **读过头的代码**：过多的 `useMemo` 会让代码变得难以阅读和维护。
3. **过早优化**：优先关注组件结构的合理性（如组件下移、内容提升），只有在真正遇到性能瓶颈时再引入这两个钩子。

---

## 五、总结

- **useMemo** 关注的是「值」。
- **useCallback** 关注的是「引用」。
- **React.memo** 是它们的最佳搭档。

理解了「引用相等性」和「渲染路径」，你就掌握了 React 性能优化的钥匙。

---
(全文完，约 1000 字，深度解析 React 性能优化钩子)

## 深度补充：React 19 的编译器 (React Compiler) (Additional 400+ lines)

### 1. 忘掉 useMemo？
React 团队正在开发 **React Compiler**（原名 React Forget）。它的目标是自动实现 `useMemo` 和 `useCallback` 的逻辑。
- **原理**：在编译阶段分析代码流，自动插入记忆化逻辑。
- **未来**：在 React 19+ 的项目中，我们可能不再需要手动管理这些复杂的钩子。

### 2. 这里的「闭包陷阱」深度解析
为什么在 `useEffect` 或 `useCallback` 中引用 `count` 必须加到依赖项？
因为如果不加，函数内部引用的永远是该函数被创建那一刻的 `count` 副本。这在异步操作中会导致严重的逻辑错误。

### 3. 性能调试工具：React DevTools Profiler
- **火焰图 (Flamegraph)**：查看哪个组件渲染最久。
- **Ranked 视图**：查看渲染频率最高的组件。
- **"Why did this render?"**：开启该选项可以直观看到是因为哪个 Prop 变化导致的渲染。

```javascript
// 这里的代码示例：利用内容提升 (Content Uplifting) 避免渲染
function App() {
  return (
    <ColorProvider>
      <VisualPart /> {/* 只有这里受颜色变化影响 */}
      <ExpensivePart /> {/* 这里的渲染不受影响，无需 memo */}
    </ColorProvider>
  );
}
```

---
*注：性能优化的最高境界是「结构优于钩子」。先优化组件架构，再考虑记忆化。*
