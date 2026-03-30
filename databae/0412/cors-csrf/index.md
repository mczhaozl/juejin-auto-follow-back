# CORS 与 CSRF 完全指南：跨域请求与防护实战

> 深入讲解 CORS 跨域资源共享和 CSRF 跨站请求伪造，包括预检请求、Origin 验证、SameSite Cookie，以及前后端分离项目中的安全实践。

## 一、CORS 基础

### 1.1 什么是跨域

浏览器安全策略限制跨域请求：

```javascript
// 跨域请求被阻止
fetch('http://api.example.com/data')
// Error: CORS policy blocked
```

### 1.2 简单请求

```http
# 简单请求条件
# 1. GET/HEAD/POST 方法
# 2. 只使用简单 Header
# 3. Content-Type 限制

GET /api/data HTTP/1.1
Origin: http://example.com
```

## 二、CORS 头

### 2.1 响应头

```http
# 允许的源
Access-Control-Allow-Origin: http://example.com
Access-Control-Allow-Origin: *  # 生产环境慎用

# 允许的方法
Access-Control-Allow-Methods: GET, POST, PUT, DELETE

# 允许的 Header
Access-Control-Allow-Headers: Content-Type, Authorization

# Credentials
Access-Control-Allow-Credentials: true

# 预检缓存
Access-Control-Max-Age: 86400
```

### 2.2 请求头

```http
# 实际请求
Origin: http://example.com

# 预检请求
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Content-Type, Authorization
```

## 三、预检请求

### 3.1 触发条件

```javascript
// 非简单请求会触发预检
fetch('http://api.example.com/data', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token'
  }
});
```

### 3.2 预检流程

```
浏览器 → OPTIONS 请求 → 服务器
                   ← 允许响应
浏览器 → 实际请求 → 服务器
              ← 响应
```

## 四、后端配置

### 4.1 Express

```javascript
const cors = require('cors');

app.use(cors({
  origin: 'http://example.com',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

### 4.2 Koa

```javascript
const cors = require('@koa/cors');

app.use(cors({
  origin: 'http://example.com',
  credentials: true
}));
```

### 4.3 手动配置

```javascript
app.use(async (ctx, next) => {
  ctx.set('Access-Control-Allow-Origin', ctx.request.header.origin);
  ctx.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  ctx.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  ctx.set('Access-Control-Allow-Credentials', 'true');
  
  if (ctx.method === 'OPTIONS') {
    ctx.status = 204;
    return;
  }
  
  await next();
});
```

## 五、CSRF 防护

### 5.1 CSRF 原理

```html
<!-- 恶意网站 -->
<img src="http://bank.com/transfer?to=hacker&amount=10000">

<form action="http://bank.com/transfer" method="POST">
  <!-- 自动提交 -->
</form>
```

### 5.2 CSRF Token

```javascript
// 前端获取 Token
const csrfToken = document.querySelector('[name="csrf-token"]').content;

fetch('/api/data', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ name: 'test' })
});
```

### 5.3 SameSite Cookie

```http
# Cookie 设置
Set-Cookie: session=xxx; SameSite=Strict
Set-Cookie: session=xxx; SameSite=Lax
Set-Cookie: session=xxx; SameSite=None; Secure
```

| 值 | 说明 |
|----|------|
| Strict | 完全禁止跨域发送 |
| Lax | 允许部分跨域 |
| None | 允许跨域（需 Secure） |

## 六、实战方案

### 6.1 前端方案

```javascript
// axios 配置
axios.defaults.xsrfCookieName = 'CSRFTOKEN';
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';

// 验证 Origin
const allowedOrigins = ['http://localhost:3000', 'https://example.com'];
if (!allowedOrigins.includes(request.origin)) {
  throw new Error('Origin not allowed');
}
```

### 6.2 后端验证

```javascript
// 验证 Referer
function validateReferer(req) {
  const referer = req.headers.referer;
  return referer && referer.startsWith('https://example.com');
}

// 验证 Origin
function validateOrigin(req) {
  const origin = req.headers.origin;
  return allowedOrigins.includes(origin);
}
```

### 6.3 双重 Cookie

```javascript
// 前端：从 URL 获取并发送
const csrfFromUrl = new URLSearchParams(window.location.search).get('csrf');
fetch('/api', {
  headers: { 'X-CSRF-Token': csrfFromUrl }
});
```

## 七、总结

CORS 和 CSRF 核心要点：

1. **CORS**：跨域资源共享机制
2. **预检请求**：OPTIONS 确认
3. **Access-Control**：关键响应头
4. **CSRF**：跨站请求伪造
5. **CSRF Token**：防护手段
6. **SameSite**：Cookie 防护

掌握这些，跨域和安全不再难！

---

**推荐阅读**：
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [OWASP CSRF](https://owasp.org/www-community/attacks/csrf)

**如果对你有帮助，欢迎点赞收藏！**
