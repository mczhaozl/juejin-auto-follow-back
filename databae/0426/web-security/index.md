# Web 安全完全指南

Web 安全是开发中最重要的部分之一。本文将带你从基础到高级，全面掌握 Web 安全。

## 一、常见安全威胁

### 1. XSS（跨站脚本攻击）

```javascript
// 反射型 XSS
// URL: /search?q=<script>alert('XSS')</script>
app.get('/search', (req, res) => {
  res.send(`Results for: ${req.query.q}`); // ❌ 危险
});

// 存储型 XSS
// 用户输入: <script>stealCookies()</script>
app.post('/comment', (req, res) => {
  db.save(req.body.comment); // ❌ 危险
});

// DOM 型 XSS
// URL: /#user=<script>alert('XSS')</script>
document.getElementById('user').innerHTML = location.hash.slice(1); // ❌ 危险

// 防御: 转义输出
const escapeHtml = (str) => {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
};

app.get('/search', (req, res) => {
  res.send(`Results for: ${escapeHtml(req.query.q)}`); // ✅ 安全
});

// 使用库: DOMPurify
import DOMPurify from 'dompurify';

const clean = DOMPurify.sanitize(userInput);

// 设置 Content-Security-Policy
// HTTP 头
Content-Security-Policy: default-src 'self'; script-src 'self'

// Meta 标签
<meta http-equiv="Content-Security-Policy" content="default-src 'self'">

// 设置 HttpOnly 和 Secure Cookie
res.cookie('session', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict'
});
```

### 2. SQL 注入

```javascript
// ❌ 危险
app.get('/user/:id', (req, res) => {
  const sql = `SELECT * FROM users WHERE id = ${req.params.id}`;
  db.query(sql); // SQL 注入!
});

// ❌ 危险
app.get('/user/:name', (req, res) => {
  const sql = `SELECT * FROM users WHERE name = '${req.params.name}'`;
  db.query(sql); // SQL 注入!
});

// ✅ 安全: 参数化查询
app.get('/user/:id', (req, res) => {
  const sql = 'SELECT * FROM users WHERE id = ?';
  db.query(sql, [req.params.id]);
});

// ✅ 安全: 使用 ORM
const User = require('./models/User');
app.get('/user/:id', async (req, res) => {
  const user = await User.findByPk(req.params.id);
});

// ✅ 安全: 输入验证
const { id } = req.params;
if (!/^\d+$/.test(id)) {
  return res.status(400).send('Invalid ID');
}
```

### 3. CSRF（跨站请求伪造）

```javascript
// 攻击场景: 用户登录了 bank.com
// 访问 evil.com，evil.com 有:
// <img src="https://bank.com/transfer?to=attacker&amount=1000">

// 防御: CSRF Token
// 服务器端
app.get('/form', (req, res) => {
  const csrfToken = generateToken();
  req.session.csrfToken = csrfToken;
  res.render('form', { csrfToken });
});

app.post('/submit', (req, res) => {
  if (req.body.csrfToken !== req.session.csrfToken) {
    return res.status(403).send('Invalid CSRF token');
  }
  // 处理请求
});

// 客户端
<form action="/submit" method="POST">
  <input type="hidden" name="csrfToken" value="<%= csrfToken %>">
  <input type="text" name="data">
  <button type="submit">Submit</button>
</form>

// 使用 SameSite Cookie
res.cookie('session', token, {
  sameSite: 'strict', // 或 'lax'
  httpOnly: true,
  secure: true
});

// 使用 CSRF 库
const csrf = require('csurf');
app.use(csrf({ cookie: true }));
```

### 4. 路径遍历

```javascript
// ❌ 危险
app.get('/file', (req, res) => {
  const filename = req.query.filename;
  res.sendFile(`/files/${filename}`); // ../../etc/passwd
});

// ✅ 安全: path.normalize
const path = require('path');
app.get('/file', (req, res) => {
  const filename = req.query.filename;
  const safePath = path.normalize(`/files/${filename}`);
  if (!safePath.startsWith('/files/')) {
    return res.status(403).send('Access denied');
  }
  res.sendFile(safePath);
});

// ✅ 安全: path.resolve
const safePath = path.resolve('/files', filename);
if (!safePath.startsWith('/files/')) {
  return res.status(403).send('Access denied');
}

// ✅ 安全: 白名单
const allowedFiles = ['file1.txt', 'file2.txt'];
if (!allowedFiles.includes(filename)) {
  return res.status(403).send('Access denied');
}
```

### 5. 命令注入

```javascript
// ❌ 危险
app.get('/ping', (req, res) => {
  const host = req.query.host;
  exec(`ping ${host}`, (error, stdout) => {
    res.send(stdout); // host=google.com; rm -rf /
  });
});

// ✅ 安全: 参数化
const { spawn } = require('child_process');
app.get('/ping', (req, res) => {
  const host = req.query.host;
  const ping = spawn('ping', [host]);
  ping.stdout.pipe(res);
});

// ✅ 安全: 输入验证
if (!/^[a-zA-Z0-9.-]+$/.test(host)) {
  return res.status(400).send('Invalid host');
}

// ✅ 安全: 白名单
const allowedHosts = ['google.com', 'example.com'];
if (!allowedHosts.includes(host)) {
  return res.status(403).send('Access denied');
}
```

## 二、认证和授权

### 1. 密码安全

```javascript
// ❌ 危险: 明文存储
app.post('/register', (req, res) => {
  const { password } = req.body;
  db.save({ password }); // ❌
});

// ❌ 危险: 简单哈希
const crypto = require('crypto');
const hash = crypto.createHash('md5').update(password).digest('hex'); // ❌

// ✅ 安全: bcrypt
const bcrypt = require('bcrypt');
const saltRounds = 12;

// 哈希密码
const hashedPassword = await bcrypt.hash(password, saltRounds);

// 验证密码
const isValid = await bcrypt.compare(password, hashedPassword);

// ✅ 安全: Argon2
const argon2 = require('argon2');

const hashedPassword = await argon2.hash(password);
const isValid = await argon2.verify(hashedPassword, password);
```

### 2. JWT（JSON Web Token）

```javascript
const jwt = require('jsonwebtoken');

// 生成 Token
const token = jwt.sign(
  { userId: user.id },
  process.env.JWT_SECRET,
  { expiresIn: '1h' }
);

// 验证 Token
app.use((req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).send('Unauthorized');
  }
  
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = payload.userId;
    next();
  } catch (error) {
    return res.status(401).send('Invalid token');
  }
});

// 使用短期 Token + 刷新 Token
const accessToken = jwt.sign({ userId: user.id }, SECRET, { expiresIn: '15m' });
const refreshToken = jwt.sign({ userId: user.id }, REFRESH_SECRET, { expiresIn: '7d' });

// 刷新 Token
app.post('/refresh', (req, res) => {
  const { refreshToken } = req.body;
  try {
    const payload = jwt.verify(refreshToken, REFRESH_SECRET);
    const accessToken = jwt.sign({ userId: payload.userId }, SECRET, { expiresIn: '15m' });
    res.send({ accessToken });
  } catch (error) {
    res.status(401).send('Invalid refresh token');
  }
});

// 最佳实践
// - 使用 HTTPS
// - 设置 HttpOnly Cookie
// - 短期访问 Token
// - 刷新 Token
// - Token 黑名单（可选）
```

### 3. OAuth 2.0

```javascript
// Passport.js OAuth
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: '/auth/google/callback'
  },
  (accessToken, refreshToken, profile, done) => {
    User.findOrCreate({ googleId: profile.id }, (err, user) => {
      return done(err, user);
    });
  }
));

app.get('/auth/google', passport.authenticate('google', { scope: ['profile'] }));

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    res.redirect('/');
  }
);
```

### 4. 会话管理

```javascript
const session = require('express-session');
const MongoStore = require('connect-mongo');

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({ mongoUrl: process.env.MONGODB_URI }),
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000 // 1 day
  }
}));

// 登出
app.post('/logout', (req, res) => {
  req.session.destroy(err => {
    if (err) {
      return res.status(500).send('Logout failed');
    }
    res.clearCookie('connect.sid');
    res.send('Logged out');
  });
});
```

## 三、安全头

```javascript
const helmet = require('helmet');

app.use(helmet());

// Content-Security-Policy
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "trusted-cdn.com"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "trusted-images.com"],
    fontSrc: ["'self'"],
    connectSrc: ["'self'", "api.trusted.com"],
    objectSrc: ["'none'"],
    frameSrc: ["'none'"],
    formAction: ["'self'"]
  }
}));

// X-Content-Type-Options
app.use(helmet.xContentTypeOptions());

// X-Frame-Options
app.use(helmet.frameguard({ action: 'deny' }));

// X-XSS-Protection
app.use(helmet.xssFilter());

// Strict-Transport-Security
app.use(helmet.hsts({
  maxAge: 31536000, // 1 year
  includeSubDomains: true,
  preload: true
}));

// Referrer-Policy
app.use(helmet.referrerPolicy({ policy: 'strict-origin-when-cross-origin' }));

// Permissions-Policy
app.use(helmet.permissionsPolicy({
  features: {
    geolocation: ["'none'"],
    microphone: ["'none'"],
    camera: ["'none'"]
  }
}));
```

## 四、输入验证

```javascript
// 使用 Joi
const Joi = require('joi');

const userSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(30)
    .required(),
  password: Joi.string()
    .pattern(new RegExp('^[a-zA-Z0-9]{3,30}$'))
    .required(),
  email: Joi.string()
    .email()
    .required(),
  age: Joi.number()
    .integer()
    .min(18)
    .max(120)
});

app.post('/user', (req, res) => {
  const { error, value } = userSchema.validate(req.body);
  if (error) {
    return res.status(400).send(error.details);
  }
  // 处理验证后的数据
});

// 使用 Zod
const { z } = require('zod');

const userSchema = z.object({
  username: z.string()
    .min(3)
    .max(30)
    .regex(/^[a-zA-Z0-9_]+$/),
  password: z.string()
    .min(8)
    .regex(/[a-z]/)
    .regex(/[A-Z]/)
    .regex(/[0-9]/),
  email: z.string().email(),
  age: z.number().int().min(18).max(120)
});

app.post('/user', (req, res) => {
  try {
    const user = userSchema.parse(req.body);
    // 处理验证后的数据
  } catch (error) {
    return res.status(400).send(error.errors);
  }
});
```

## 五、文件上传安全

```javascript
const multer = require('multer');

// ❌ 危险
const upload = multer({ dest: 'uploads/' });
app.post('/upload', upload.single('file'), (req, res) => {
  // 任何文件都可以上传
});

// ✅ 安全
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + '-' + file.originalname);
  }
});

const fileFilter = (req, file, cb) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  if (allowedTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error('Invalid file type'), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB
  }
});

app.post('/upload', upload.single('file'), (req, res) => {
  // 验证文件内容
  const sharp = require('sharp');
  try {
    await sharp(req.file.path).metadata();
    res.send('File uploaded');
  } catch (error) {
    fs.unlinkSync(req.file.path);
    res.status(400).send('Invalid image');
  }
});
```

## 六、依赖安全

```bash
# 检查漏洞
npm audit
npm audit fix

# 使用 Snyk
npm install -g snyk
snyk test
snyk monitor

# 使用 npm ci 而非 npm install
npm ci

# 锁定版本
# package-lock.json
# yarn.lock

# 定期更新依赖
npm outdated
npm update
```

## 七、日志和监控

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// 记录安全事件
app.post('/login', (req, res) => {
  logger.info('Login attempt', { ip: req.ip, username: req.body.username });
  
  if (loginFailed) {
    logger.warn('Login failed', { ip: req.ip, username: req.body.username });
  }
});

// 速率限制
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // 100 requests
});

app.use('/api/', limiter);

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 login attempts
  message: 'Too many login attempts'
});

app.post('/login', loginLimiter, (req, res) => {
  // 处理登录
});
```

## 八、最佳实践检查清单

- [ ] 防御 XSS（转义输出、CSP、HttpOnly Cookie）
- [ ] 防御 SQL 注入（参数化查询、ORM）
- [ ] 防御 CSRF（CSRF Token、SameSite Cookie）
- [ ] 防御路径遍历（path.normalize、白名单）
- [ ] 防御命令注入（参数化、输入验证）
- [ ] 安全的密码存储（bcrypt、Argon2）
- [ ] 安全的认证（JWT、OAuth、会话管理）
- [ ] 设置安全头（CSP、HSTS、X-Frame-Options）
- [ ] 输入验证（Joi、Zod）
- [ ] 安全的文件上传（类型验证、大小限制）
- [ ] 定期检查依赖漏洞
- [ ] 日志和监控
- [ ] 速率限制
- [ ] 使用 HTTPS

## 九、总结

Web 安全核心要点：
- 常见威胁（XSS、SQLi、CSRF、路径遍历、命令注入）
- 认证和授权（密码安全、JWT、OAuth、会话管理）
- 安全头（CSP、HSTS、X-Frame-Options 等）
- 输入验证
- 文件上传安全
- 依赖安全
- 日志和监控
- 最佳实践

开始构建安全的 Web 应用吧！
