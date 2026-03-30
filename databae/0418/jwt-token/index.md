# JWT 完全指南：JSON Web Token 实战

> 深入讲解 JWT 令牌机制，包括 JWT 结构、签名算法、刷新策略，以及实际项目中的安全存储、黑名单和性能优化。

## 一、JWT 基础

### 1.1 什么是 JWT

JSON Web Token：

```
┌─────────────────────────────────────────────────────────────┐
│                      JWT 结构                                │
│                                                              │
│  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.                   │
│  ──────────────────────────────                             │
│  Header (头部)                                              │
│                                                              │
│  eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaW   │
│  ──────────────────────────────                             │
│  Payload (负载)                                             │
│                                                              │
│  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c             │
│  ──────────────────────────────                             │
│  Signature (签名)                                           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 JWT 组成

```javascript
// Header
{
  "alg": "HS256",  // 算法
  "typ": "JWT"
}

// Payload
{
  "sub": "1234567890",
  "name": "张三",
  "admin": true,
  "iat": 1516239022,    // 签发时间
  "exp": 1516242622     // 过期时间
}

// Signature
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
```

## 二、算法

### 2.1 对称算法

```javascript
// HMAC (HS256)
const jwt = require('jsonwebtoken')

// 生成
const token = jwt.sign(
  { userId: 123 },
  'my-secret-key',
  { expiresIn: '1h' }
)

// 验证
const decoded = jwt.verify(token, 'my-secret-key')
```

### 2.2 非对称算法

```javascript
const jwt = require('jsonwebtoken')
const fs = require('fs')

// 读取密钥
const privateKey = fs.readFileSync('private.key')
const publicKey = fs.readFileSync('public.key')

// 用私钥生成
const token = jwt.sign(
  { userId: 123 },
  privateKey,
  { algorithm: 'RS256', expiresIn: '1h' }
)

// 用公钥验证
const decoded = jwt.verify(token, publicKey, {
  algorithms: ['RS256']
})
```

### 2.3 算法对比

| 算法 | 类型 | 用途 |
|------|------|------|
| HS256 | 对称 | 小型应用 |
| RS256 | 非对称 | 大型应用 |
| ES256 | 非对称 | 椭圆曲线 |

## 三、使用

### 3.1 生成令牌

```javascript
const jwt = require('jsonwebtoken')

// 基本使用
const token = jwt.sign(
  {
    userId: 123,
    username: 'zhangsan',
    role: 'admin'
  },
  process.env.JWT_SECRET,
  {
    expiresIn: '7d',        // 7天
    issuer: 'myapp'         // 签发者
  }
)

// 过期时间设置
jwt.sign(payload, secret, {
  expiresIn: '1h'           // 1小时
  expiresIn: '7d'           // 7天
  expiresIn: '2h30m'        // 2小时30分
})
```

### 3.2 验证令牌

```javascript
// 验证并解码
try {
  const decoded = jwt.verify(token, process.env.JWT_SECRET)
  console.log(decoded.userId)
} catch (err) {
  if (err.name === 'TokenExpiredError') {
    console.log('Token 已过期')
  } else if (err.name === 'JsonWebTokenError') {
    console.log('Token 无效')
  }
}

// 只解码不验证
const decoded = jwt.decode(token)
```

## 四、刷新策略

### 4.1 Access Token + Refresh Token

```
┌─────────────────────────────────────────────────────────────┐
│                    令牌刷新策略                              │
│                                                              │
│  1. 登录 ──▶ 返回 access_token + refresh_token            │
│                                                              │
│  2. 访问 ──▶ access_token (过期)                          │
│                                                              │
│  3. 刷新 ──▶ 用 refresh_token 换新的 access_token        │
│                                                              │
│  4. 继续访问                                                │
│                                                              │
│  5. refresh_token 也过期 ──▶ 重新登录                     │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 实现

```javascript
const jwt = require('jsonwebtoken')
const crypto = require('crypto')

// 生成令牌对
function generateTokens(userId) {
  const accessToken = jwt.sign(
    { userId, type: 'access' },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  )
  
  const refreshToken = crypto.randomBytes(40).toString('hex')
  
  // 存储 refresh token
  redis.setex(`refresh:${userId}`, 7 * 24 * 3600, refreshToken)
  
  return { accessToken, refreshToken }
}

// 刷新令牌
function refreshTokens(refreshToken) {
  // 验证 refresh token
  const userId = redis.get(`refresh:${refreshToken}`)
  if (!userId) {
    throw new Error('Invalid refresh token')
  }
  
  // 生成新令牌
  return generateTokens(userId)
}

// 验证 access token
function verifyAccessToken(token) {
  return jwt.verify(token, process.env.JWT_SECRET)
}
```

## 五、安全最佳实践

### 5.1 最佳实践

```javascript
// 1. 使用强密钥
const secret = crypto.randomBytes(32).toString('hex')

// 2. 设置过期时间
jwt.sign(payload, secret, { expiresIn: '1h' })

// 3. 验证必要字段
jwt.verify(token, secret, {
  algorithms: ['HS256'],  // 指定算法
  issuer: 'myapp',         // 验证签发者
  subject: 'user'          // 验证主题
})

// 4. 存储安全
// - 不要存储在 localStorage
// - 使用 HttpOnly Cookie
// - HTTPS 传输
```

### 5.2 常见问题

| 问题 | 解决方案 |
|------|----------|
| Token 泄露 | 短期 access + 黑名单 |
| 重放攻击 | 一次性使用 + 时间戳 |
| 算法篡改 | 指定 algorithms |
| 密钥泄露 | 定期轮换 |

## 六、黑名单

### 6.1 实现

```javascript
const jwt = require('jsonwebtoken')
const redis = require('redis')

const redisClient = redis.createClient()

// 登出时加入黑名单
async function logout(token) {
  const decoded = jwt.decode(token)
  const exp = decoded.exp - Date.now() / 1000
  if (exp > 0) {
    await redisClient.setex(`blacklist:${token}`, exp, '1')
  }
}

// 验证时检查黑名单
async function verify(token, secret) {
  const isBlacklisted = await redisClient.get(`blacklist:${token}`)
  if (isBlacklisted) {
    throw new Error('Token is blacklisted')
  }
  
  return jwt.verify(token, secret)
}
```

## 七、实战案例

### 7.1 Express 中间件

```javascript
const jwt = require('jsonwebtoken')

const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '')
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' })
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    req.user = decoded
    next()
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' })
    }
    return res.status(401).json({ error: 'Invalid token' })
  }
}

// 使用
app.get('/api/profile', authMiddleware, (req, res) => {
  res.json({ user: req.user })
})
```

### 7.2 Cookie 存储

```javascript
// 设置 HttpOnly Cookie
app.post('/login', (req, res) => {
  const token = jwt.sign({ userId: 123 }, process.env.JWT_SECRET, {
    expiresIn: '7d'
  })
  
  res.cookie('token', token, {
    httpOnly: true,
    secure: true,          // HTTPS only
    sameSite: 'strict',    // CSRF 防护
    maxAge: 7 * 24 * 3600 * 1000
  })
  
  res.json({ success: true })
})

// 读取 Cookie
app.get('/api/profile', (req, res) => {
  const token = req.cookies.token
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    res.json({ user: decoded })
  } catch (err) {
    res.status(401).json({ error: 'Unauthorized' })
  }
})
```

## 八、总结

JWT 核心要点：

1. **结构**：Header/Payload/Signature
2. **算法**：HS256/RS256
3. **刷新**：Access + Refresh
4. **安全**：HTTPS/黑名单
5. **存储**：HttpOnly Cookie
6. **验证**：issuer/subject

掌握这些，身份认证 so easy！

---

**推荐阅读**：
- [JWT 官方文档](https://jwt.io/)
- [RFC 7519](https://tools.ietf.org/html/rfc7519)

**如果对你有帮助，欢迎点赞收藏！**
