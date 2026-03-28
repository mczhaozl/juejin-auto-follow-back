# Web Push API：在浏览器中实现原生级推送通知

> 谁说只有原生 App 才能发送推送通知？Web Push API 正在打破 Web 与原生应用的最后一道围墙。本文将带你深度实战 Web Push 与 Service Worker，为你的 Web 应用开启全天候的消息推送能力。

---

## 目录 (Outline)
- [一、 Web 通知的演进：从「轮询」到「实时推送」](#一-web-通知的演进从轮询到实时推送)
- [二、 Web Push API 核心：Service Worker 与推送服务](#二-web-push-api-核心service-worker-与推送服务)
- [三、 快速上手：获取用户许可与生成订阅对象](#三-快速上手获取用户许可与生成订阅对象)
- [四、 后端实战：VAPID 协议与推送消息的发送](#四-后端实战vapid-协议与推送消息的发送)
- [五、 Service Worker 监听：接收、显示与点击处理](#五-service-worker-监听接收显示与点击处理)
- [六、 进阶：离线消息与通知内容的个性化定制](#六-进阶离线消息与通知内容的个性化定制)
- [七、 总结：Web Push 对 PWA 的核心价值](#七-总结web-push-对-pwa-的核心价值)

---

## 一、 Web 通知的演进：从「轮询」到「实时推送」

### 1. 历史局限
过去，Web 页面要获取新消息，只能依靠：
- **短轮询**：每隔几秒请求一次服务器。
- **WebSocket**：虽然实时，但页面关闭后连接即断开。

### 2. 标志性事件
- **2015 年**：Chrome 42 正式引入 Web Push。
- **2023 年**：iOS 16.4 正式在 Safari 中支持 Web Push，标志着该技术在移动端的全平台普及。

---

## 二、 Web Push API 核心：Service Worker 与推送服务

Web Push 的精妙之处在于它**不需要**浏览器标签页处于打开状态。

### 工作流程
1. **浏览器订阅**：用户授权后，浏览器从「推送服务商 (Push Service)」获取一个 Endpoint。
2. **保存订阅**：前端将 Endpoint 发送给你的服务器。
3. **服务器推送**：你的服务器通过推送服务商发送消息。
4. **唤醒 SW**：浏览器后台接收消息，唤醒 Service Worker，由 SW 显示通知。

---

## 三、 快速上手：获取用户许可与生成订阅对象

### 前端代码示例
```javascript
async function subscribeUser() {
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
  });
  
  // 发送订阅对象到后端
  await fetch('/api/save-subscription', {
    method: 'POST',
    body: JSON.stringify(subscription),
    headers: { 'Content-Type': 'application/json' }
  });
}
```

---

## 四、 后端实战：VAPID 协议与推送消息的发送

为了防止滥用，Web Push 使用 **VAPID** 协议进行身份验证。

### Node.js 发送示例
```javascript
const webpush = require('web-push');

webpush.setVapidDetails(
  'mailto:example@yourdomain.com',
  publicVapidKey,
  privateVapidKey
);

// 推送消息
webpush.sendNotification(subscription, JSON.stringify({
  title: '新消息提醒',
  body: '您有一条新的系统通知，请查收！'
}));
```

---

## 五、 Service Worker 监听：接收、显示与点击处理

这是 Web Push 的最后一步。

### Service Worker 代码
```javascript
self.addEventListener('push', (event) => {
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: '/img/icon.png',
    badge: '/img/badge.png',
    data: { url: 'https://example.com' }
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// 点击通知跳转
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
```

---

## 六、 进阶：离线消息与通知内容的个性化定制

Web Push 支持丰富的配置：
- **震动模式 (Vibrate)**：[200, 100, 200]。
- **动作按钮 (Actions)**：允许用户直接在通知栏回复或确认。
- **静默推送**：只同步数据而不显示通知。

---

## 七、 总结：Web Push 对 PWA 的核心价值

Web Push 是 PWA（渐进式 Web 应用）最重要的特性之一。它让 Web 应用具备了**用户召回**的能力，极大地提升了用户留存。

---
> 关注我，深挖 Web 标准与 PWA 技术实战，带你打造媲美原生体验的 Web 应用。
