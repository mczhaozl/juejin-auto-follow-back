# Chrome DevTools Protocol: 实战网络弱网模拟与精准 Mock

> 在自动化测试和复杂前端调试中，仅仅依靠浏览器的 UI 界面是不够的。本文将带你深入 CDP (Chrome DevTools Protocol) 协议，实战如何在代码层面实现精细的网络弱网模拟与接口 Mock。

---

## 目录 (Outline)
- [一、 超越 UI 调试：为什么我们需要编程控制浏览器？](#一-超越-ui-调试为什么我们需要编程控制浏览器)
- [二、 CDP 协议核心：Network 域与 Fetch 域](#二-cdp-协议核心network-域与-fetch-域)
- [三、 实战 1：利用 CDP 模拟「极度弱网」与「离线」场景](#三-实战-1利用-cdp-模拟极度弱网与离线场景)
- [四、 实战 2：精细化的请求拦截与 Response Mock](#四-实战-2精细化的请求拦截与-response-mock)
- [五、 自动化测试集成：Puppeteer 与 Playwright 的 CDP 接口](#五-自动化测试集成puppeteer-与-playwright-的-cdp-接口)
- [六、 性能监控进阶：通过 CDP 获取未被压缩的资源大小](#六-性能监控进阶通过-cdp-获取未被压缩的资源大小)
- [七、 总结：掌握浏览器底层控制的「金钥匙」](#七-总结掌握浏览器底层控制的金钥匙)

---

## 一、 超越 UI 调试：为什么我们需要编程控制浏览器？

### 1. 痛点：手动模拟的局限性
在 Chrome DevTools 的 Network 面板里，虽然可以设置「Fast 3G」或「Slow 3G」，但它是**全局**的。

### 2. 自动化需求
在 CI/CD 流程中，我们需要自动测试：
- 弱网环境下首页加载是否超时？
- 接口返回 500 时，前端是否显示了正确的错误状态？
- 模拟特定域名下的资源加载失败。

这些都需要通过编程手段来实现。

---

## 二、 CDP 协议核心：Network 域与 Fetch 域

CDP 是浏览器内部的一种通信协议。在网络控制方面，有两个核心域：

1. **Network 域**：负责监听请求信息、模拟网络状况（带宽、延迟）。
2. **Fetch 域**：负责拦截、修改请求和响应。

---

## 三、 实战 1：利用 CDP 模拟「极度弱网」与「离线」场景

使用 Puppeteer 开启 CDP 会话。

### 代码实现
```javascript
const client = await page.target().createCDPSession();

// 开启 Network 域
await client.send('Network.enable');

// 模拟极度弱网 (Slow 2G 级别)
await client.send('Network.emulateNetworkConditions', {
  offline: false,
  latency: 2000,      // 2秒延迟
  downloadThroughput: 50 * 1024 / 8, // 50kbps
  uploadThroughput: 20 * 1024 / 8,   // 20kbps
});

// 如果要模拟离线
// await client.send('Network.emulateNetworkConditions', { offline: true, ... });
```

---

## 四、 实战 2：精细化的请求拦截与 Response Mock

相比于全局代理，`Fetch.enable` 允许我们根据正则表达式精准拦截特定请求。

### 实现步骤
1. **监听请求**：
   ```javascript
   await client.send('Fetch.enable', {
     patterns: [{ urlPattern: '*/api/user/*', requestStage: 'Request' }]
   });
   ```
2. **修改响应**：
   ```javascript
   client.on('Fetch.requestPaused', async (event) => {
     // 拦截到请求，直接返回自定义数据
     await client.send('Fetch.fulfillRequest', {
       requestId: event.requestId,
       responseCode: 200,
       responseHeaders: [{ name: 'Content-Type', value: 'application/json' }],
       body: Buffer.from(JSON.stringify({ name: 'Mocked User' })).toString('base64'),
     });
   });
   ```

---

## 五、 自动化测试集成：Puppeteer 与 Playwright 的 CDP 接口

虽然 Puppeteer 和 Playwright 都提供了更高级的 `page.route` 封装，但在某些极端场景（如处理 Service Worker 拦截的请求、或修改底层 TCP 参数）下，直接调用 `CDPSession` 依然是不可替代的。

---

## 六、 性能监控进阶：通过 CDP 获取未被压缩的资源大小

有时候我们需要知道资源在 Gzip/Brotli 压缩前的原始大小，以进行更精准的包体积优化。

```javascript
await client.send('Network.getResponseBody', { requestId });
// 这将返回解码后的内容
```

---

## 七、 总结：掌握浏览器底层控制的「金钥匙」

CDP 不仅仅是调试工具，它更像是一把「金钥匙」，让我们能够穿透浏览器的高级封装，直接操控底层引擎。掌握了 CDP，你就具备了构建复杂自动化测试框架、性能分析工具甚至自研浏览器的基础能力。

---
> 关注我，深挖浏览器内核黑科技，让你的技术栈更具底层竞争力。
