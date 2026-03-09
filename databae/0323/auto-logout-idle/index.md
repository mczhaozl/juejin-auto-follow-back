# 用户无操作自动退出登录的实现方案

> 通过监听用户交互事件和定时器，实现 10 分钟无操作自动退出登录的完整方案。

---

## 一、为什么需要自动退出

在企业级应用中，自动退出登录是常见的安全需求：

- 防止用户离开后他人操作账号
- 满足合规要求（如金融、医疗系统）
- 减少服务器 session 占用

核心思路是：监听用户交互 → 重置计时器 → 超时后执行退出。

## 二、实现思路

### 核心逻辑

1. 监听用户的鼠标、键盘等交互事件
2. 每次交互重置倒计时
3. 超过设定时间（如 10 分钟）无交互，执行退出

### 需要考虑的点

- 哪些事件算「用户操作」
- 多标签页同步问题
- 退出前的提示
- 接口调用是否算活跃

## 三、基础实现

### 1. 单页面版本

```javascript
class AutoLogout {
  constructor(timeout = 10 * 60 * 1000) { // 默认 10 分钟
    this.timeout = timeout;
    this.timer = null;
    this.events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    this.init();
  }

  init() {
    // 绑定事件监听
    this.events.forEach(event => {
      document.addEventListener(event, this.resetTimer.bind(this), true);
    });
    
    // 启动计时器
    this.resetTimer();
  }

  resetTimer() {
    // 清除旧计时器
    if (this.timer) {
      clearTimeout(this.timer);
    }
    
    // 设置新计时器
    this.timer = setTimeout(() => {
      this.logout();
    }, this.timeout);
  }

  logout() {
    console.log('用户无操作，自动退出登录');
    // 清除 token
    localStorage.removeItem('token');
    // 跳转到登录页
    window.location.href = '/login';
  }

  destroy() {
    // 清理事件监听
    this.events.forEach(event => {
      document.removeEventListener(event, this.resetTimer.bind(this), true);
    });
    if (this.timer) {
      clearTimeout(this.timer);
    }
  }
}

// 使用
const autoLogout = new AutoLogout(10 * 60 * 1000);
```

### 2. React Hook 版本

```javascript
import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

function useAutoLogout(timeout = 10 * 60 * 1000) {
  const navigate = useNavigate();
  const timerRef = useRef(null);

  useEffect(() => {
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];

    const resetTimer = () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }

      timerRef.current = setTimeout(() => {
        // 退出登录
        localStorage.removeItem('token');
        navigate('/login');
      }, timeout);
    };

    // 初始化
    resetTimer();

    // 绑定事件
    events.forEach(event => {
      document.addEventListener(event, resetTimer, true);
    });

    // 清理
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, resetTimer, true);
      });
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [timeout, navigate]);
}

// 在根组件使用
function App() {
  useAutoLogout(10 * 60 * 1000);
  return <div>...</div>;
}
```

## 四、进阶优化

### 1. 多标签页同步

使用 localStorage 事件实现多标签页同步：

```javascript
class AutoLogoutWithSync {
  constructor(timeout = 10 * 60 * 1000) {
    this.timeout = timeout;
    this.timer = null;
    this.storageKey = 'last_activity_time';
    this.init();
  }

  init() {
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    
    events.forEach(event => {
      document.addEventListener(event, this.updateActivity.bind(this), true);
    });

    // 监听其他标签页的活动
    window.addEventListener('storage', this.onStorageChange.bind(this));

    this.startCheck();
  }

  updateActivity() {
    // 更新最后活动时间
    localStorage.setItem(this.storageKey, Date.now().toString());
  }

  onStorageChange(e) {
    // 其他标签页有活动，重置本页计时器
    if (e.key === this.storageKey) {
      this.startCheck();
    }
  }

  startCheck() {
    if (this.timer) {
      clearInterval(this.timer);
    }

    // 每秒检查一次
    this.timer = setInterval(() => {
      const lastActivity = parseInt(localStorage.getItem(this.storageKey) || '0');
      const now = Date.now();

      if (now - lastActivity > this.timeout) {
        this.logout();
      }
    }, 1000);
  }

  logout() {
    clearInterval(this.timer);
    localStorage.removeItem('token');
    localStorage.removeItem(this.storageKey);
    window.location.href = '/login';
  }
}
```

### 2. 退出前倒计时提示

```javascript
class AutoLogoutWithWarning {
  constructor(timeout = 10 * 60 * 1000, warningTime = 60 * 1000) {
    this.timeout = timeout;
    this.warningTime = warningTime; // 提前 1 分钟提示
    this.timer = null;
    this.warningTimer = null;
    this.init();
  }

  resetTimer() {
    if (this.timer) clearTimeout(this.timer);
    if (this.warningTimer) clearTimeout(this.warningTimer);

    // 提前提示
    this.warningTimer = setTimeout(() => {
      this.showWarning();
    }, this.timeout - this.warningTime);

    // 最终退出
    this.timer = setTimeout(() => {
      this.logout();
    }, this.timeout);
  }

  showWarning() {
    const remainingSeconds = Math.floor(this.warningTime / 1000);
    const confirmed = confirm(
      `您已 ${Math.floor(this.timeout / 60000)} 分钟未操作，` +
      `将在 ${remainingSeconds} 秒后自动退出。点击确定继续使用。`
    );

    if (confirmed) {
      this.resetTimer(); // 用户选择继续
    }
  }

  logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
}
```

### 3. 接口请求也算活跃

如果希望用户调用接口也算活跃操作：

```javascript
// 在 axios 拦截器中更新活动时间
axios.interceptors.request.use(config => {
  // 更新最后活动时间
  localStorage.setItem('last_activity_time', Date.now().toString());
  return config;
});
```

## 五、注意事项

### 1. 事件选择

- 常用事件：`mousedown`、`keydown`、`scroll`、`touchstart`
- 不建议用 `mousemove`：触发太频繁，影响性能
- 移动端记得加 `touchstart`、`touchmove`

### 2. 性能优化

```javascript
// 使用节流避免频繁重置
import { throttle } from 'lodash';

const resetTimer = throttle(() => {
  // 重置逻辑
}, 1000); // 1 秒内最多触发一次
```

### 3. 退出前清理

```javascript
logout() {
  // 1. 清除本地存储
  localStorage.removeItem('token');
  localStorage.removeItem('userInfo');
  
  // 2. 清除 cookie（如果有）
  document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
  
  // 3. 调用后端退出接口
  fetch('/api/logout', { method: 'POST' })
    .finally(() => {
      window.location.href = '/login';
    });
}
```

### 4. 开发环境跳过

```javascript
constructor(timeout = 10 * 60 * 1000) {
  // 开发环境不启用自动退出
  if (process.env.NODE_ENV === 'development') {
    return;
  }
  this.timeout = timeout;
  this.init();
}
```

## 总结

实现自动退出登录的关键点：

- 监听用户交互事件（鼠标、键盘、触摸）
- 使用定时器控制超时逻辑
- 多标签页用 localStorage + storage 事件同步
- 退出前可加倒计时提示提升体验
- 注意性能优化（节流）和开发环境处理

根据实际需求选择合适的方案，基础版本适合简单场景，多标签页同步和提示功能适合企业级应用。
