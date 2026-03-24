# React 生态：掌握 useOptimistic 实现零延迟的交互体验

> React 19 带来了许多激动人心的新特性，其中 useOptimistic 是提升用户体验的利器。本文将带你深入理解如何利用它在异步操作完成前，立即更新界面，实现「秒开」级别的交互效果。

## 一、什么是乐观更新 (Optimistic UI)？

在处理网络请求时，通常的流程是：用户点击 -> 发送请求 -> 等待 -> 服务器响应 -> 更新界面。这在网络环境差时，用户会感到明显的「卡顿」。

**乐观更新**则是在发送请求的同时，先假设请求会成功，并立即更新界面。如果请求最终失败，再回滚到之前的状态。

## 二、主角：useOptimistic Hook

`useOptimistic` 是 React 19 提供的专门用于处理乐观更新的 Hook。

### 1. 基本语法
```javascript
const [optimisticState, addOptimistic] = useOptimistic(
  state, // 基础状态
  (currentState, optimisticValue) => {
    // 根据当前状态和乐观值，返回新的乐观状态
    return [...currentState, optimisticValue];
  }
);
```

### 2. 实战案例：发送消息

```javascript
import { useOptimistic, useState } from 'react';

function ChatApp({ messages, sendMessage }) {
  // 1. 定义基础状态
  const [dbMessages, setDbMessages] = useState(messages);

  // 2. 定义乐观状态
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    dbMessages,
    (state, newMessage) => [...state, { text: newMessage, sending: true }]
  );

  async function formAction(formData) {
    const messageText = formData.get("message");
    
    // 3. 立即触发乐观更新
    addOptimisticMessage(messageText);

    // 4. 发送真实请求
    const savedMessage = await sendMessage(messageText);
    
    // 5. 更新真实状态（完成后，React 会自动回滚乐观状态并显示真实状态）
    setDbMessages(prev => [...prev, savedMessage]);
  }

  return (
    <>
      {optimisticMessages.map((m, i) => (
        <div key={i}>
          {m.text} {m.sending && <small>(Sending...)</small>}
        </div>
      ))}
      <form action={formAction}>
        <input type="text" name="message" />
        <button type="submit">Send</button>
      </form>
    </>
  );
}
```

## 三、为什么不直接用 useState？

虽然用 `useState` 也能实现类似效果，但 `useOptimistic` 有几个核心优势：
- **自动回滚**：当异步操作结束（通常在 `action` 完成后），React 会自动弃用乐观状态，切换回真实状态。
- **并发安全**：在多个并发操作时，React 能正确合并多个乐观更新。
- **代码结构清晰**：专门用于处理「临时」状态，不污染长期业务逻辑。

## 四、总结

`useOptimistic` 并不是新概念，但在 React 19 中，它被内置化并标准化了。这能极大地提升我们应用的响应速度和专业感。

**如果你对 React 19 的表单处理（Actions）感兴趣，欢迎查阅我之前的文章！**
