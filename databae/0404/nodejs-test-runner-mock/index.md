# Node.js 22+: 深入理解内置测试运行器的 Mock 与 Coverage 功能

> 长期以来，Node.js 生态中的测试一直被 Jest、Mocha 和 Vitest 等第三方框架统治。然而，从 Node.js 20 开始引入，并在 22 版本中趋于完善的内置测试运行器（`node:test`），正在以极致的性能和零依赖的优势改变这一局面。本文将带你深度实战内置测试框架的高级特性：Mock、计时器模拟以及代码覆盖率统计。

---

## 目录 (Outline)
- [一、 为什么选择原生测试运行器？](#一-为什么选择原生测试运行器)
- [二、 核心实战 1：深度 Mock 机制与函数追踪](#二-核心实战-1深度-mock-机制与函数追踪)
- [三、 核心实战 2：计时器模拟 (Timer Mocking)](#三-核心实战-2计时器模拟-timer-mocking)
- [四、 性能与覆盖率：内置 Coverage 的使用技巧](#四-性能与覆盖率内置-coverage-的使用技巧)
- [五、 总结与迁移建议](#五-总结与迁移建议)

---

## 一、 为什么选择原生测试运行器？

### 1. 历史背景
在过去，为了跑一个简单的单元测试，我们需要：
1. 安装 `jest` 及其庞大的依赖树（通常几百 MB）。
2. 配置 `jest.config.js`。
3. 处理 CJS/ESM 的转译问题。

### 2. 原生优势
- **启动速度**：无需转译，直接在 Node.js 进程中运行，冷启动时间几乎为零。
- **零配置**：`node --test` 即可自动扫描测试文件。
- **稳定性**：作为 Node.js 核心库的一部分，永远不会出现版本不兼容的「灵异 Bug」。

---

## 二、 核心实战 1：深度 Mock 机制与函数追踪

`node:test` 模块内置了一个强大的 `mock` 对象，支持对方法、属性进行拦截。

### 代码示例：Mock 外部 API 调用
```javascript
import test from 'node:test';
import assert from 'node:assert';

test('测试 API 调用逻辑', async (t) => {
  const userService = {
    fetchUser: async (id) => ({ id, name: 'Real User' })
  };

  // 1. 创建一个 Mock 函数
  t.mock.method(userService, 'fetchUser', async (id) => {
    return { id, name: 'Mocked User' };
  });

  const user = await userService.fetchUser(1);
  
  // 2. 断言结果
  assert.strictEqual(user.name, 'Mocked User');
  
  // 3. 检查调用历史
  assert.strictEqual(userService.fetchUser.mock.calls.length, 1);
  assert.strictEqual(userService.fetchUser.mock.calls[0].arguments[0], 1);
});
```

---

## 三、 核心实战 2：计时器模拟 (Timer Mocking)

测试包含 `setTimeout` 或 `setInterval` 的代码时，等待真实时间是非常低效的。

### 实战代码
```javascript
import test from 'node:test';
import assert from 'node:assert';

test('测试防抖逻辑', (t) => {
  // 开启计时器 Mock
  t.mock.timers.enable();
  
  let called = false;
  setTimeout(() => { called = true; }, 1000);

  // 立即将时间推进 1000ms
  t.mock.timers.tick(1000);
  
  assert.strictEqual(called, true);
});
```

---

## 四、 性能与覆盖率：内置 Coverage 的使用技巧

Node.js 22 进一步优化了内置的代码覆盖率报告。

### 如何生成报告？
无需安装 `istanbul` 或 `nyc`，直接运行：
```bash
node --test --experimental-test-coverage
```

### 进阶：指定覆盖率阈值
虽然目前 Node.js 还没内置「阈值拦截」，但你可以配合简单的脚本读取生成的覆盖率 JSON 来实现 CI 拦截。

---

## 五、 总结与迁移建议

- **适用场景**：对于纯 Node.js 后端服务、CLI 工具、或追求极致构建速度的微服务，`node:test` 是不二之选。
- **局限性**：如果你需要复杂的 JSDOM 模拟（前端组件测试）或丰富的可视化报告，Jest 依然更强大。
- **建议**：新项目尝试从原生测试起步。你会发现，摆脱了那几百兆的测试依赖后，开发体验从未如此清爽。

Node.js 正在通过补齐这些「基础基建」，向一个更完整、更现代的开发平台进化。

---

> **参考资料：**
> - *Node.js Documentation: Test runner*
> - *Testing in Node.js: The Native Way*
> - *Performance Comparison: Node:test vs Jest*
