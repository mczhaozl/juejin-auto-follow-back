# 从微信小程序 data-id 到 React 列表性能优化：少用闭包，多用 data-*

> 以小程序里常见的 data-* 传参为引子，讲 React 列表里「闭包 + map」对 memo/虚拟化的影响，以及用 data-* 单函数的优化写法。

---

## 一、从微信小程序 data-id 说起

写微信小程序时，列表项点击通常不会给每个 item 绑一个闭包，而是用 **data-*** 把 id 挂在节点上，在**一个**事件处理函数里从 `event.currentTarget.dataset` 取出来：

```javascript
// 小程序 WXML 常见写法
<block wx:for="{{items}}" wx:key="id">
  <view data-id="{{item.id}}" bindtap="onItemTap">{{item.name}}</view>
</block>
// JS: 一个 onItemTap，从 event.currentTarget.dataset.id 取 id
```

这样做的原因之一是小程序端对「同一函数引用」更友好，列表更新时不会因为每项都绑了新函数而产生多余开销。  
回到 **React**，我们却经常在列表里写「每个 item 一个闭包」——写法简单，但在大列表或配合 memo、虚拟化时，就会暴露出性能与优化难度问题。下面先说常见写法的问题，再给出与小程序思路一致的替代方案。

---

## 二、React 里的常见写法：.map() 中的闭包

假设你在渲染一个列表，每项可点击并需要把 `item.id` 传给处理函数：

```jsx
{items.map((item) => (
  <button key={item.id} onClick={() => handleClick(item.id)}>
    {item.name}
  </button>
))}
```

这种方式**简洁、好写**，效果也没问题：每次点击都能拿到正确的 `item.id`。  
但背后有一个事实：**每次组件渲染时，你都在为列表中的每一项创建一个新的函数**——一个捕获了当前 `item.id` 的闭包。在大多数小列表场景下，这不会有明显影响；一旦列表变长、或你开始做「减少重渲染」的优化，这种写法就会成为障碍。

---

## 三、闭包的潜在弊端

闭包是 JavaScript 和 React 的核心概念，但在 **.map() 里为每项创建一个新函数** 可能带来这些问题：

### 1. 破坏 memo / useCallback 与虚拟化

- 若子组件用 **React.memo** 包裹，或父组件用 **useCallback** 把回调传给子组件，优化依赖的是**函数引用稳定**。而 `onClick={() => handleClick(item.id)}` 在每次父组件渲染时都会生成新的函数引用，**子组件会认为 props 变了**，于是本可避免的重渲染会发生，记忆化就失效了。
- 若使用**虚拟列表**（如 react-window、react-virtualized），只渲染可见项，同样依赖「回调引用稳定」或至少「不因列表数据引用变就全量更新」。每项一个闭包会导致每次父组件渲染时，所有可见项的 onClick 都是新引用，虚拟化的收益被削弱。

### 2. 大列表下优化难度增加

当列表很长、交互频繁时，**最小化重渲染**变得很重要。内联闭包让「一个列表共用一个事件处理函数」变得困难，你很难在保持可读性的前提下，既用闭包又配合 memo/虚拟化做细粒度优化。

---

## 四、替代方案：用 data-* 单函数，与小程序殊途同归

与其为每个 item 创建一个闭包，不如像小程序那样：**把标识（如 id）放在 DOM 的 data 属性上，只写一个事件处理函数**，在函数里从 `event.currentTarget.dataset` 读取。

```jsx
// 单一事件处理函数，引用稳定
function handleClick(e) {
  const id = e.currentTarget.dataset.id;
  console.log("Clicked item:", id);
  // 后续用 id 做请求、跳转等
}

{items.map((item) => (
  <button key={item.id} data-id={item.id} onClick={handleClick}>
    {item.name}
  </button>
))}
```

**优势**：

- **单一函数引用** → 父组件重渲染时，`handleClick` 不变（若用 `function` 声明或配合 `useCallback` 无依赖，引用更稳定），**React.memo** 或 **useCallback** 能真正生效，子组件不会因为「回调换了」而重渲染。
- **大列表、虚拟列表** 下，事件逻辑集中在一个函数里，更容易配合虚拟化做性能优化。
- **事件逻辑集中**，代码更清晰；从「每个 item 绑一个闭包」变成「一个 handleClick + data-id」，和小程序的 data-* 用法一致，跨端经验可以复用。

注意：`data-id` 在 DOM 上会变成 **data-id**（小写）；在 React 里写 `data-id={item.id}`，通过 `e.currentTarget.dataset.id` 读取即可。若需要传复杂数据，可只传 id，在 handler 里用 id 从 state/context/缓存中取详情，避免在 DOM 上挂大对象。

---

## 五、总结

- **小程序** 里常用 **data-*** 把 id 绑在节点上，用一个事件处理函数从 `dataset` 取 id，避免为每项创建新回调。
- **React** 里在 `.map()` 中写 `onClick={() => handleClick(item.id)}` 会在每次渲染时为每项创建新闭包，容易**破坏 React.memo、useCallback 和虚拟列表**的优化，大列表下优化难度增加。
- **替代方案**：用 **data-id**（或其它 data-*）把 id 挂在 DOM 上，只写一个 **handleClick(e)**，在内部用 `e.currentTarget.dataset.id` 取 id；单一函数引用，便于 memo 与虚拟化，事件逻辑更集中，与小程序写法一致。

若对你有用，欢迎点赞、收藏；你们在 React 或小程序里若有类似的列表点击优化实践，也欢迎在评论区分享。
