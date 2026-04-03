# Web 安全完全指南：OWASP Top 10 与实战防御

Web 安全是每个开发者必须掌握的技能。本文将带你深入了解 OWASP Top 10 和常见攻击的防御方法。

## 一、OWASP Top 10 2021

### 1. A01:2021 - 访问控制失效 (Broken Access Control)

```javascript
// ❌ 危险：直接使用用户输入的 ID
app.get('/api/users/:id', (req, res) => {
  const user = db.findUser(req.params.id);
  res.json(user); // 任何人都可以访问任何用户
});

// ✅ 安全：验证用户权限
app.get('/api/users/:id', (req, res) => {
  if (req.user.id !== req.params.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Access denied' });
  }
  const user = db.findUser(req.params.id);
  res.json(user);
});
```

### 2. A02:2021 - 加密失败 (Cryptographic Failures)

```javascript
// ❌ 危险：使用弱加密
const crypto = require('crypto');
const cipher = crypto.createCipher('aes192', 'password'); // 废弃的 API

// ❌ 危险：硬编码密钥
const secret = 'my-secret-key-123'; // 不要提交到代码库！

// ✅ 安全：使用环境变量和强加密
require('dotenv').config();
const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');

function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag().toString('hex');
  return { iv: iv.toString('hex'), encrypted, authTag };
}
```

### 3. A03:2021 - 注入 (Injection)

```javascript
// ❌ 危险：SQL 注入
app.get('/api/users', (req, res) => {
  const query = `SELECT * FROM users WHERE name = '${req.query.name}'`;
  db.query(query); // 危险！
});

// ✅ 安全：使用参数化查询
app.get('/api/users', (req, res) => {
  const query = 'SELECT * FROM users WHERE name = $1';
  db.query(query, [req.query.name]);
});

// ❌ 危险：命令注入
app.get('/api/files', (req, res) => {
  exec(`ls ${req.query.path}`); // 危险！
});

// ✅ 安全：避免命令注入
const fs = require('fs');
app.get('/api/files', (req, res) => {
  const safePath = path.join(__dirname, 'files', path.basename(req.query.path));
  fs.readdir(safePath, (err, files) => {
    res.json(files);
  });
});
```

### 4. A04:2021 - 不安全设计 (Insecure Design)

```javascript
// ❌ 危险：在客户端验证
if (user.isAdmin) {
  showAdminPanel(); // 客户端可以被篡改
}

// ✅ 安全：始终在服务端验证
app.get('/api/admin', (req, res) => {
  if (!req.user.isAdmin) {
    return res.status(403).json({ error: 'Access denied' });
  }
  res.json(adminData);
});
```

### 5. A05:2021 - 安全配置错误 (Security Misconfiguration)

```yaml
# ❌ 危险：使用默认配置
debug: true
secret_key: default-secret

# ✅ 安全：生产环境配置
debug: false
secret_key: ${SECRET_KEY}
security:
  cors:
    allowed_origins:
      - https://your-app.com
  headers:
    x-frame-options: DENY
    x-content-type-options: nosniff
```

### 6. A06:2021 - 易受攻击和过时的组件 (Vulnerable and Outdated Components)

```bash
# 检查依赖漏洞
npm audit
npm audit fix

# 使用工具
snyk test
owasp-dependency-check

# 定期更新
npm outdated
npm update
```

### 7. A07:2021 - 识别和认证失效 (Identification and Authentication Failures)

```javascript
// ❌ 危险：弱密码
app.post('/api/register', (req, res) => {
  const user = {
    username: req.body.username,
    password: req.body.password // 直接存储明文密码！
  };
});

// ✅ 安全：强密码哈希
const bcrypt = require('bcrypt');
const saltRounds = 12;

app.post('/api/register', async (req, res) => {
  const hashedPassword = await bcrypt.hash(req.body.password, saltRounds);
  const user = {
    username: req.body.username,
    password: hashedPassword
  };
});

app.post('/api/login', async (req, res) => {
  const user = await db.findUser(req.body.username);
  const match = await bcrypt.compare(req.body.password, user.password);
  if (!match) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
});
```

### 8. A08:2021 - 软件和数据完整性失效 (Software and Data Integrity Failures)

```javascript
// ❌ 危险：使用未验证的脚本
<script src="https://untrusted-cdn.com/script.js"></script>

// ✅ 安全：使用 SRI
<script 
  src="https://cdn.example.com/script.js"
  integrity="sha384-abc123..."
  crossorigin="anonymous"
></script>

// ✅ 安全：验证 JWT
const jwt = require('jsonwebtoken');
app.get('/api/protected', (req, res) => {
  try {
    const token = req.headers.authorization.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    res.json(decoded);
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
});
```

### 9. A09:2021 - 安全日志和监控失效 (Security Logging and Monitoring Failures)

```javascript
// ✅ 安全：记录安全事件
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

app.post('/api/login', (req, res) => {
  logger.info('Login attempt', { username: req.body.username });
  
  if (!valid) {
    logger.warn('Failed login', { username: req.body.username, ip: req.ip });
  }
});
```

### 10. A10:2021 - 服务端请求伪造 (Server-Side Request Forgery, SSRF)

```javascript
// ❌ 危险：SSRF
app.get('/api/fetch', (req, res) => {
  fetch(req.query.url) // 用户可以指定内部 URL
    .then(response => response.json())
    .then(data => res.json(data));
});

// ✅ 安全：白名单验证
const allowedHosts = ['api.example.com', 'cdn.example.com'];

app.get('/api/fetch', (req, res) => {
  const url = new URL(req.query.url);
  if (!allowedHosts.includes(url.hostname)) {
    return res.status(400).json({ error: 'Invalid URL' });
  }
  fetch(req.query.url)
    .then(response => response.json())
    .then(data => res.json(data));
});
```

## 二、常见攻击与防御

### 1. XSS (跨站脚本攻击)

```javascript
// ❌ 危险：直接插入用户输入
const userContent = '<script>alert("XSS")</script>';
document.getElementById('content').innerHTML = userContent;

// ✅ 安全：使用 textContent
document.getElementById('content').textContent = userContent;

// ✅ 安全：转义 HTML
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ✅ 安全：使用 CSP
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self'; style-src 'self'"
  );
  next();
});
```

### 2. CSRF (跨站请求伪造)

```javascript
// ❌ 危险：没有 CSRF 保护
app.post('/api/transfer', (req, res) => {
  transferMoney(req.body.to, req.body.amount);
});

// ✅ 安全：使用 CSRF Token
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.get('/api/csrf-token', csrfProtection, (req, res) => {
  res.json({ csrfToken: req.csrfToken() });
});

app.post('/api/transfer', csrfProtection, (req, res) => {
  transferMoney(req.body.to, req.body.amount);
});

// ✅ 安全：使用 SameSite Cookie
app.use(cookieParser());
app.use(session({
  cookie: {
    sameSite: 'strict',
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true
  }
}));
```

### 3. 路径遍历

```javascript
// ❌ 危险：路径遍历
app.get('/api/files', (req, res) => {
  fs.readFile(req.query.filename); // ../../etc/passwd
});

// ✅ 安全：验证路径
const path = require('path');
app.get('/api/files', (req, res) => {
  const filename = req.query.filename;
  const safePath = path.normalize(filename);
  
  if (safePath.includes('..')) {
    return res.status(400).json({ error: 'Invalid path' });
  }
  
  const fullPath = path.join(__dirname, 'files', safePath);
  fs.readFile(fullPath, (err, data) => {
    res.send(data);
  });
});
```

### 4. 暴力破解

```javascript
// ✅ 安全：速率限制
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 5, // 限制 5 次
  message: 'Too many login attempts'
});

app.post('/api/login', loginLimiter, (req, res) => {
  // 登录逻辑
});

// ✅ 安全：账户锁定
let loginAttempts = {};

app.post('/api/login', (req, res) => {
  const username = req.body.username;
  
  if (loginAttempts[username] >= 5) {
    return res.status(429).json({ error: 'Account locked' });
  }
  
  if (!valid) {
    loginAttempts[username] = (loginAttempts[username] || 0) + 1;
  } else {
    loginAttempts[username] = 0;
  }
});
```

## 三、HTTP 安全头

```javascript
const helmet = require('helmet');
app.use(helmet());

// 或手动设置
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Permissions-Policy', 'geolocation=(), microphone=()');
  next();
});
```

## 四、安全最佳实践

1. 永远不要信任用户输入
2. 验证所有数据
3. 使用参数化查询
4. 加密敏感数据
5. 使用 HTTPS
6. 实施安全的认证
7. 实施访问控制
8. 记录和监控
9. 保持依赖更新
10. 定期安全审计

## 五、总结

Web 安全要点：
- 掌握 OWASP Top 10
- 防御常见攻击（XSS、CSRF、注入等）
- 使用安全的 HTTP 头
- 验证和转义所有用户输入
- 加密敏感数据
- 定期更新依赖
- 实施日志和监控

安全无小事，时刻保持警惕！
