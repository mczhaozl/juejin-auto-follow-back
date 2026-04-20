# 前端安全与防护完全指南：从 XSS 到 CSRF 全面防护

## 一、XSS 防护

### 1.1 反射型 XSS

```javascript
// 不好：直接渲染用户输入
document.getElementById('result').innerHTML = userInput;

// 好：转义输出
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

document.getElementById('result').innerHTML = escapeHtml(userInput);
```

### 1.2 存储型 XSS

```javascript
// 服务端保存前进行验证和过滤
// 使用内容安全策略（CSP）
```

```html
<!-- Content-Security-Policy 头 -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' https://trusted-cdn.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data:;
">
```

---

## 二、CSRF 防护

```javascript
// 1. 使用 SameSite Cookie
Set-Cookie: session=abc; SameSite=Strict; Secure; HttpOnly;

// 2. CSRF Token
const token = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/action', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': token
  }
});
```

---

## 三、点击劫持防护

```html
<!-- X-Frame-Options -->
<meta http-equiv="X-Frame-Options" content="SAMEORIGIN">

<!-- Content-Security-Policy frame-ancestors -->
<meta http-equiv="Content-Security-Policy" content="frame-ancestors 'self'">
```

---

## 四、内容安全策略（CSP）

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-abc123' https://trusted.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
```

```javascript
// 使用 nonce
const nonce = 'abc123'; // 服务器生成
document.querySelector('script[nonce]').nonce = nonce;
```

---

## 五、安全头配置

```http
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## 六、输入验证与输出编码

```javascript
// 输入验证
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// 输出编码
function encodeForHTML(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}

function encodeForURL(str) {
  return encodeURIComponent(str);
}
```

---

## 七、React/Vue 安全

```jsx
// React：JSX 自动转义
// 好
<div>{userInput}</div>

// 不好（除非必要）
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// Vue：自动转义
// 好
<div>{{ userInput }}</div>

// 不好
<div v-html="userInput"></div>
```

---

## 八、依赖安全

```bash
# 检查依赖漏洞
npm audit

# 升级有漏洞的依赖
npm audit fix

# 使用 Snyk
npm install -g snyk
snyk test
```

---

## 九、HTTPS 与 HSTS

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

---

## 十、本地存储安全

```javascript
// 不好：存储敏感信息
localStorage.setItem('password', 'secret');

// 好：使用 HttpOnly Cookie
Set-Cookie: token=abc; Secure; HttpOnly; SameSite=Strict

// 好：必要时加密
const encrypted = encrypt(data, key);
localStorage.setItem('data', encrypted);
```

---

## 十一、最佳实践

1. 始终进行输入验证
2. 输出编码防止 XSS
3. 使用 Content-Security-Policy
4. 设置安全的 HTTP 头
5. 使用 HTTPS

---

## 十二、总结

前端安全需要开发、服务端、运维一起努力，构建纵深防御。
