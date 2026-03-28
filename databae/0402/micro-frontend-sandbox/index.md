# 微前端沙箱深度剖析：从 Proxy 隔离到 Shadow Realm 的演进

> 在微前端（Micro Frontends）架构中，沙箱（Sandbox）是确保多个独立应用在同一个页面内和谐共存的关键技术。从最初的简单闭包，到 qiankun 广泛使用的 Proxy 沙箱，再到未来的 Shadow Realm 提案，沙箱技术经历了一场深度的底层变革。本文将带你深度剖析微前端沙箱的实现原理。

---

## 目录 (Outline)
- [一、 沙箱的核心使命：解决什么问题？](#一-沙箱的核心使命解决什么问题)
- [二、 进阶历程 1：基于 Proxy 的运行时隔离](#二-进阶历程-1基于-proxy-的运行时隔离)
- [三、 进阶历程 2：CSS 隔离的痛点与方案](#三-进阶历程-2css-隔离的痛点与方案)
- [四、 未来已来：Shadow Realm 提案如何重塑隔离？](#四-未来已来shadow-realm-提案如何重塑隔离)
- [五、 总结与选型建议](#五-总结与选型建议)

---

## 一、 沙箱的核心使命：解决什么问题？

微前端沙箱主要解决两个维度的冲突：
1. **全局变量污染**：子应用 A 修改了 `window.history`，不能影响到子应用 B。
2. **副作用残留**：子应用卸载后，其开启的 `setInterval` 或绑定的全局事件必须被清除。

---

## 二、 进阶历程 1：基于 Proxy 的运行时隔离

目前主流微前端框架（如 qiankun, Garfish）的核心方案。

### 1. 单实例沙箱 (SnapshotSandbox)
在子应用挂载前快照记录 `window`，卸载时恢复。
- **缺点**：性能差，且无法支持多个子应用同时运行。

### 2. 多实例沙箱 (ProxySandbox)
通过 `new Proxy(window, ...)` 为每个子应用创建一个「伪全局对象」。

### 3. 实战代码示例（简易 Proxy 沙箱）
```javascript
class ProxySandbox {
  constructor(name) {
    this.name = name;
    this.proxyWindow = {};
    const rawWindow = window;
    
    this.proxy = new Proxy(this.proxyWindow, {
      set(target, prop, value) {
        // 子应用的修改只写到伪对象中
        target[prop] = value;
        return true;
      },
      get(target, prop) {
        // 优先从伪对象读，读不到再从真实 window 读
        return target[prop] || rawWindow[prop];
      }
    });
  }
}

const sandboxA = new ProxySandbox('appA');
sandboxA.proxy.token = 'secret_a';

const sandboxB = new ProxySandbox('appB');
console.log(sandboxB.proxy.token); // undefined (完美隔离！)
```

---

## 三、 进阶历程 2：CSS 隔离的痛点与方案

JS 隔离了，样式冲突怎么办？

### 1. 动态样式表切换
在子应用挂载时插入 `<style>`，卸载时移除。
- **缺点**：无法解决多个子应用同时在线时的样式污染。

### 2. Shadow DOM (Strict Isolation)
真正的硬隔离。将子应用挂载在 `Shadow Root` 下。
- **优点**：浏览器原生的样式隔离。
- **缺点**：一些基于 `body` 的弹出层（如 Select 菜单）定位会失效。

---

## 四、 未来已来：Shadow Realm 提案如何重塑隔离？

`Shadow Realm` 是 ECMAScript 的一个 Stage 3 提案，旨在提供一个全新的、完全隔离的 JS 执行环境。

### 1. 核心优势
- **同步执行**：不同于 Worker 的异步通信，Shadow Realm 内部代码执行是同步的。
- **内存安全**：它拥有独立的堆栈，无法直接访问主环境的全局对象（甚至没有 `window`）。

### 2. 代码示例（前瞻）
```javascript
const realm = new ShadowRealm();

// 在独立环境内运行代码，并返回结果
const result = await realm.importValue('./app-bundle.js', 'main');
result();
```

---

## 五、 总结与选型建议

- **生产环境 (现在)**：优先使用 **qiankun (Proxy + 动态样式表)**。它最成熟，社区生态最丰富。
- **追求极致性能**：考虑 **Web Worker 隔离**（如 Alfajs），将非 UI 逻辑移出主线程。
- **技术储备**：关注 **Shadow Realm** 规范。一旦浏览器原生支持，微前端的隔离性能将达到质的飞跃。

微前端沙箱的进化史，本质上是 Web 应用从「共享环境」向「受控沙盒」转型的历史。理解了沙箱，你就掌握了微前端架构的底层逻辑。

---

> **参考资料：**
> - *qiankun source code: ProxySandbox implementation*
> - *MDN: Shadow DOM API*
> - *TC39 Proposal: ShadowRealm*
