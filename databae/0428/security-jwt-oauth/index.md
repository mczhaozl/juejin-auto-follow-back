# JWT 与 OAuth 2.0 完全安全指南：从理论到实现

## 一、JWT 概述

JSON Web Token (JWT) 是一种无状态的认证令牌。

### 1.1 JWT 结构

```
Header.Payload.Signature
```

```json
// Header（算法、类型）
{ "alg": "HS256", "typ": "JWT" }

// Payload（声明）
{ "sub": "12345", "name": "John Doe", "exp": 1680000000 }

// Signature（签名）
HMACSHA256( base64UrlEncode(header) + "." + base64UrlEncode(payload), secret )
```

### 1.2 标准声明 (Claims)

| 声明 | 描述 |
|-----|------|
| iss | 签发者 |
| sub | 主题 |
| aud | 受众 |
| exp | 过期时间 |
| nbf | 生效时间 |
| iat | 签发时间 |
| jti | JWT ID |

---

## 二、JWT 实现

### 2.1 Node.js 实现

```javascript
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

// 生成
function generateToken(userId) {
  const payload = {
    sub: userId,
    iat: Date.now(),
    exp: Date.now() + 24 * 60 * 60 * 1000
  };
  
  return jwt.sign(payload, process.env.JWT_SECRET, {
    algorithm: 'HS256'
  });
}

// 验证
function verifyToken(token) {
  try {
    return jwt.verify(token, process.env.JWT_SECRET);
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      throw new Error('Token expired');
    }
    throw new Error('Invalid token');
  }
}
```

### 2.2 使用非对称加密

```javascript
import jwt from 'jsonwebtoken';
import fs from 'fs';

const privateKey = fs.readFileSync('private.key');
const publicKey = fs.readFileSync('public.key');

const token = jwt.sign(payload, privateKey, { algorithm: 'RS256' });
const decoded = jwt.verify(token, publicKey, { algorithms: ['RS256'] });
```

---

## 三、JWT 安全最佳实践

### 3.1 短过期时间

```javascript
const accessToken = jwt.sign(payload, secret, { expiresIn: '15m' });
const refreshToken = jwt.sign(payload, refreshSecret, { expiresIn: '7d' });
```

### 3.2 使用 HTTPS

```javascript
// 设置 Cookie 为 Secure、HttpOnly、SameSite=Strict
res.cookie('token', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
  maxAge: 15 * 60 * 1000
});
```

### 3.3 防止敏感信息

```javascript
// Payload 不存密码、SSN 等敏感信息
const payload = {
  userId: user.id,  // 只放 ID
  role: user.role
};
```

---

## 四、OAuth 2.0 流程

### 4.1 四种授权类型

| 类型 | 场景 |
|-----|------|
| Authorization Code | Web 应用（服务端渲染） |
| Client Credentials | 机器对机器（M2M） |
| Implicit | SPA（不推荐） |
| Password | 高度信任的应用 |

### 4.2 Authorization Code Flow

```
(1) 用户点击登录
    → 重定向到 /authorize?response_type=code&client_id=...
(2) 用户授权
    → 重定向回 redirect_uri?code=xxx
(3) 后端换 token
    → POST /token (code + client_secret)
    → 返回 access_token + refresh_token
```

---

## 五、OAuth 2.0 实现

### 5.1 Node.js 简单服务器

```javascript
import express from 'express';
import jwt from 'jsonwebtoken';

const app = express();

// 模拟用户数据库
const users = new Map();

// (1) 授权端点
app.get('/authorize', (req, res) => {
  const { client_id, redirect_uri, response_type } = req.query;
  
  // 验证 client_id、redirect_uri...
  
  // 显示登录/授权页面
  res.send(`
    <form method="POST" action="/approve">
      <input type="hidden" name="redirect_uri" value="${redirect_uri}">
      <button type="submit">授权</button>
    </form>
  `);
});

// (2) 生成 code
app.post('/approve', (req, res) => {
  const authCode = 'random-code';
  authCodes.set(authCode, { userId: 1, clientId: req.body.client_id });
  res.redirect(`${req.body.redirect_uri}?code=${authCode}`);
});

// (3) 换 token
app.post('/token', (req, res) => {
  const { code, client_id, client_secret } = req.body;
  
  // 验证 code、client_secret...
  
  const accessToken = jwt.sign(
    { sub: authCode.userId, iss: 'my-server' },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );
  
  res.json({
    access_token: accessToken,
    token_type: 'Bearer',
    expires_in: 900,
    refresh_token: '...'
  });
});
```

---

## 六、OAuth 与 OpenID Connect

### 6.1 OIDC = OAuth + 身份认证

```json
// id_token (JWT)
{
  "iss": "https://provider.example",
  "sub": "12345",
  "aud": "client-id",
  "exp": 123456,
  "iat": 123450,
  "name": "John Doe",
  "email": "john@example.com"
}
```

---

## 七、刷新令牌

### 7.1 Refresh Token 流程

```javascript
app.post('/refresh', (req, res) => {
  const { refresh_token } = req.body;
  
  // 验证 refresh token
  const decoded = jwt.verify(refresh_token, process.env.REFRESH_SECRET);
  
  // 检查是否在黑名单中
  if (tokenBlacklist.has(refresh_token)) {
    return res.status(401).json({ error: 'Invalid token' });
  }
  
  // 生成新 token
  const newAccessToken = jwt.sign(
    { sub: decoded.sub },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );
  
  res.json({
    access_token: newAccessToken,
    token_type: 'Bearer',
    expires_in: 900
  });
});
```

---

## 八、安全清单

- [ ] 使用 RS256 而非 HS256（生产环境）
- [ ] Access Token 过期时间不超过 15-30 分钟
- [ ] Refresh Token 妥善存储（数据库）
- [ ] 使用 HTTPS 传输所有令牌
- [ ] 防止敏感信息在 JWT 中明文
- [ ] 验证签名与过期时间
- [ ] 实现 Refresh Token 轮换与黑名单

---

## 九、总结

JWT 与 OAuth 2.0 是现代认证授权的标准，正确、安全地使用它们是每个开发者的必备技能。
