# Web 安全完全指南：XSS、SQL 注入与防护策略

> 深入讲解 Web 安全，包括 XSS、SQL 注入、CSRF、点击劫持等常见攻击原理，以及实际项目中的防护策略和最佳实践。

## 一、XSS 攻击

### 1.1 什么是 XSS

跨站脚本攻击（XSS）：

```javascript
// 恶意脚本注入
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
```

### 1.2 XSS 类型

| 类型 | 说明 |
|------|------|
| 反射型 | URL 参数中的 XSS |
| 存储型 | 持久化到数据库 |
| DOM 型 | 前端代码中的漏洞 |

### 1.3 防护措施

```javascript
// 转义输出
function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Vue 自动转义
<div>{{ userInput }}</div>

// React 自动转义
<div>{userInput}</div>
```

## 二、SQL 注入

### 2.1 原理

```sql
-- 恶意输入：' OR '1'='1
SELECT * FROM users WHERE username = '' OR '1'='1'
```

### 2.2 防护措施

```python
# 参数化查询
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)
)

# ORM 查询
user = User.query.filter_by(username=username).first()
```

```javascript
// Node.js 参数化
const result = await db.query(
  'SELECT * FROM users WHERE id = $1',
  [userId]
);
```

## 三、CSRF 攻击

### 3.1 原理

```html
<!-- 恶意网站 -->
<img src="http://bank.com/transfer?to=hacker&amount=10000">

<form action="http://bank.com/transfer" method="POST">
  <input type="hidden" name="to" value="hacker">
  <input type="hidden" name="amount" value="10000">
</form>
```

### 3.2 防护措施

```javascript
// CSRF Token
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/data', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify(data)
});
```

```python
# Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
```

## 四、点击劫持

### 4.1 原理

攻击者将目标网站嵌入到透明 iframe 中：

```html
<iframe src="http://bank.com/transfer" style="opacity:0; position:absolute; top:0; left:0;">
```

### 4.2 防护

```http
# HTTP 响应头
X-Frame-Options: DENY
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: frame-ancestors 'none'
```

## 五、密码安全

### 5.1 哈希存储

```javascript
// bcrypt 加密
const bcrypt = require('bcrypt');
const saltRounds = 10;

async function hashPassword(password) {
  return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password, hash) {
  return await bcrypt.compare(password, hash);
}
```

### 5.2 密码强度

```javascript
function validatePassword(password) {
  if (password.length < 8) return false;
  if (!/[A-Z]/.test(password)) return false;
  if (!/[a-z]/.test(password)) return false;
  if (!/[0-9]/.test(password)) return false;
  return true;
}
```

## 六、HTTPS

### 6.1 强制 HTTPS

```javascript
// Express
const helmet = require('helmet');
app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: true
}));
```

### 6.2 安全 Headers

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

## 七、总结

Web 安全核心要点：

1. **XSS**：转义输出、CSP
2. **SQL 注入**：参数化查询
3. **CSRF**：Token 验证
4. **点击劫持**：X-Frame-Options
5. **密码**：bcrypt 哈希
6. **HTTPS**：强制使用

掌握这些，Web 安全有保障！

---

**推荐阅读**：
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MDN Web 安全](https://developer.mozilla.org/en-US/docs/Web/Security)

**如果对你有帮助，欢迎点赞收藏！**
