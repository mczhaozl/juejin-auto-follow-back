# 系统如何通知用户更新并刷新页面

> 介绍前端应用检测版本更新并提示用户刷新的几种实现方案，包括轮询、WebSocket 和 Service Worker。

---

## 一、为什么需要更新提示

前端应用发布新版本后，用户浏览器可能还在使用旧版本的缓存文件，导致：

- 新功能无法使用
- 接口字段变更导致报错
- 样式错乱或功能异常

常见场景：

- SPA 应用发布后，用户长时间不刷新页面
- 移动端 H5 应用被 WebView 缓存
- PWA 应用需要更新 Service Worker

## 二、方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 轮询版本号 | 简单易实现 | 有延迟，增加请求 | 中小型应用 |
| WebSocket | 实时性好 | 需要后端支持 | 需要实时通信的应用 |
| Service Worker | 离线可用，体验好 | 复杂度高 | PWA 应用 |
| ETag/Last-Modified | 利用 HTTP 缓存 | 依赖服务器配置 | 静态资源更新 |

## 三、方案一：轮询版本号

### 实现思路

1. 在 `index.html` 或单独文件中写入版本号
2. 前端定时请求版本号接口
3. 对比本地版本号，不一致则提示刷新

### 后端生成版本文件

```javascript
// build 时生成 version.json
const fs = require('fs');
const path = require('path');

const version = {
  version: Date.now().toString(), // 或者用 git commit hash
  buildTime: new Date().toISOString()
};

fs.writeFileSync(
  path.join(__dirname, 'dist/version.json'),
  JSON.stringify(version)
);
```

### 前端轮询检测

```javascript
class VersionChecker {
  constructor(interval = 5 * 60 * 1000) { // 默认 5 分钟
    this.interval = interval;
    this.currentVersion = null;
    this.timer = null;
  }

  async init() {
    // 获取当前版本
    this.currentVersion = await this.fetchVersion();
    // 开始轮询
    this.startPolling();
  }

  async fetchVersion() {
    try {
      const res = await fetch('/version.json?t=' + Date.now());
      const data = await res.json();
      return data.version;
    } catch (error) {
      console.error('获取版本号失败', error);
      return null;
    }
  }

  startPolling() {
    this.timer = setInterval(async () => {
      const latestVersion = await this.fetchVersion();
      
      if (latestVersion && latestVersion !== this.currentVersion) {
        this.notifyUpdate();
      }
    }, this.interval);
  }

  notifyUpdate() {
    const shouldUpdate = confirm(
      '检测到新版本，是否立即刷新页面？\n' +
      '（刷新后可能会丢失未保存的数据）'
    );

    if (shouldUpdate) {
      window.location.reload();
    }
  }

  destroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }
}

// 使用
const checker = new VersionChecker(5 * 60 * 1000);
checker.init();
```

### React Hook 版本

```javascript
import { useEffect, useRef, useState } from 'react';

function useVersionCheck(interval = 5 * 60 * 1000) {
  const [hasUpdate, setHasUpdate] = useState(false);
  const currentVersionRef = useRef(null);

  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const res = await fetch('/version.json?t=' + Date.now());
        const data = await res.json();
        return data.version;
      } catch (error) {
        return null;
      }
    };

    const checkVersion = async () => {
      const latestVersion = await fetchVersion();
      
      if (!currentVersionRef.current) {
        currentVersionRef.current = latestVersion;
        return;
      }

      if (latestVersion && latestVersion !== currentVersionRef.current) {
        setHasUpdate(true);
      }
    };

    // 初始化
    checkVersion();

    // 定时检查
    const timer = setInterval(checkVersion, interval);

    return () => clearInterval(timer);
  }, [interval]);

  const handleUpdate = () => {
    window.location.reload();
  };

  return { hasUpdate, handleUpdate };
}

// 在组件中使用
function App() {
  const { hasUpdate, handleUpdate } = useVersionCheck();

  return (
    <div>
      {hasUpdate && (
        <div className="update-banner">
          <span>发现新版本</span>
          <button onClick={handleUpdate}>立即更新</button>
        </div>
      )}
      {/* 其他内容 */}
    </div>
  );
}
```

## 四、方案二：WebSocket 实时推送

### 后端推送

```javascript
// Node.js + Socket.io 示例
const io = require('socket.io')(server);

// 发布新版本时广播
function notifyNewVersion(version) {
  io.emit('version:update', { version });
}
```

### 前端监听

```javascript
import io from 'socket.io-client';

class WebSocketVersionChecker {
  constructor() {
    this.socket = null;
    this.currentVersion = null;
  }

  init() {
    this.socket = io('wss://your-server.com');

    this.socket.on('connect', () => {
      console.log('WebSocket 已连接');
    });

    this.socket.on('version:update', (data) => {
      if (data.version !== this.currentVersion) {
        this.notifyUpdate(data.version);
      }
    });
  }

  notifyUpdate(newVersion) {
    const shouldUpdate = confirm(`检测到新版本 ${newVersion}，是否刷新？`);
    if (shouldUpdate) {
      window.location.reload();
    }
  }

  destroy() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}
```

## 五、方案三：Service Worker

### 注册 Service Worker

```javascript
// main.js
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
    .then(registration => {
      // 检查更新
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // 有新版本
            notifyUpdate();
          }
        });
      });

      // 定时检查更新
      setInterval(() => {
        registration.update();
      }, 60 * 60 * 1000); // 每小时检查一次
    });
}

function notifyUpdate() {
  const shouldUpdate = confirm('发现新版本，是否立即更新？');
  if (shouldUpdate) {
    window.location.reload();
  }
}
```

### Service Worker 文件

```javascript
// sw.js
const CACHE_NAME = 'v1.0.0';

self.addEventListener('install', (event) => {
  // 强制跳过等待，立即激活
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // 清理旧缓存
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

## 六、优化体验

### 1. 非侵入式提示

```javascript
// 使用 Toast 而非 confirm
function showUpdateToast() {
  const toast = document.createElement('div');
  toast.className = 'update-toast';
  toast.innerHTML = `
    <span>发现新版本</span>
    <button onclick="window.location.reload()">立即更新</button>
    <button onclick="this.parentElement.remove()">稍后</button>
  `;
  document.body.appendChild(toast);
}
```

```css
.update-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  border-radius: 4px;
  z-index: 9999;
}
```

### 2. 延迟刷新

```javascript
// 用户无操作时自动刷新
let updatePending = false;
let idleTimer = null;

function scheduleUpdate() {
  updatePending = true;
  
  // 监听用户活动
  const events = ['mousedown', 'keydown', 'scroll'];
  const resetIdle = () => {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      if (updatePending) {
        window.location.reload();
      }
    }, 30 * 1000); // 30 秒无操作则刷新
  };

  events.forEach(event => {
    document.addEventListener(event, resetIdle);
  });

  resetIdle();
}
```

### 3. 保存用户数据

```javascript
function safeReload() {
  // 保存表单数据到 localStorage
  const formData = {
    // 收集表单数据
  };
  localStorage.setItem('form_backup', JSON.stringify(formData));
  
  // 刷新
  window.location.reload();
}

// 页面加载后恢复数据
window.addEventListener('load', () => {
  const backup = localStorage.getItem('form_backup');
  if (backup) {
    // 恢复数据
    localStorage.removeItem('form_backup');
  }
});
```

## 七、注意事项

### 1. 避免频繁检查

```javascript
// 用户切换标签页时暂停检查
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    clearInterval(timer);
  } else {
    startPolling();
  }
});
```

### 2. 版本号生成策略

```javascript
// 使用 git commit hash
const { execSync } = require('child_process');
const commitHash = execSync('git rev-parse --short HEAD').toString().trim();

// 或者使用时间戳 + 随机数
const version = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
```

### 3. 缓存策略

```nginx
# nginx 配置：version.json 不缓存
location /version.json {
  add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

## 总结

选择合适的方案：

- 简单应用：轮询版本号（5-10 分钟间隔）
- 需要实时性：WebSocket 推送
- PWA 应用：Service Worker + 定时检查
- 混合方案：轮询 + 用户无操作时自动刷新

关键点：

- 版本号文件不能被缓存
- 提示要友好，避免打断用户操作
- 考虑保存用户未提交的数据
- 开发环境可以跳过检查
