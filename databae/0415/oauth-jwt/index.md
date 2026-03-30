# OAuth 2.0 与 JWT 完全指南：身份认证与授权

> 深入讲解 OAuth 2.0 授权流程和 JWT Token 机制，包括授权码模式、Access Token、Refresh Token，以及实际项目中的安全实践。

## 一、OAuth 2.0 基础

### 1.1 什么是 OAuth 2.0

开放授权标准：

```
用户 → 第三方应用 → 授权服务器 → 资源服务器
```

### 1.2 授权流程

```
1. 用户点击"使用微信登录"
2. 跳转到授权页面
3. 用户授权
4. 返回授权码
5. 用授权码换 Token
6. 使用 Token 获取资源
```

## 二、授权模式

### 2.1 授权码模式

```javascript
// 1. 跳转授权
const authUrl = `https://auth.example.com/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  response_type=code&
  scope=read&state=xyz`;

// 2. 授权后回调
// GET /callback?code=AUTHORIZATION_CODE&state=xyz

// 3. 换取 Token
const tokenResponse = await fetch('https://auth.example.com/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: 'AUTHORIZATION_CODE',
    redirect_uri: 'YOUR_REDIRECT_URI',
    client_id: 'YOUR_CLIENT_ID',
    client_secret: 'YOUR_CLIENT_SECRET'
  })
});

const { access_token, refresh_token } = await tokenResponse.json();
```

### 2.2 隐式模式

```javascript
// 不推荐，仅用于前端 SPA
const authUrl = `https://auth.example.com/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  response_type=token&
  scope=read`;
```

### 2.3 客户端模式

```javascript
// 服务端间通信
const tokenResponse = await fetch('https://auth.example.com/token', {
  method: 'POST',
  body: new URLSearchParams({
    grant_type: 'client_credentials',
    client_id: 'YOUR_CLIENT_ID',
    client_secret: 'YOUR_CLIENT_SECRET'
  })
});
```

## 三、JWT

### 3.1 JWT 结构

```
header.payload.signature
```

```javascript
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "1234567890",
  "name": "张三",
  "iat": 1516239022,
  "exp": 1516242622
}

// Signature
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

### 3.2 生成 JWT

```javascript
const jwt = require('jsonwebtoken');

const token = jwt.sign(
  { userId: 123, role: 'admin' },
  'your-secret-key',
  { expiresIn: '1h' }
);

const decoded = jwt.verify(token, 'your-secret-key');
```

### 3.3 验证 JWT

```javascript
function verifyToken(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  try {
    const decoded = jwt.verify(token, 'your-secret-key');
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

## 四、Refresh Token

### 4.1 流程

```javascript
// Access Token 过期
if (error.name === 'TokenExpiredError') {
  // 用 Refresh Token 刷新
  const newToken = await refreshAccessToken(refreshToken);
}

// 刷新 Token
async function refreshAccessToken(refreshToken) {
  const response = await fetch('https://auth.example.com/token', {
    method: 'POST',
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: 'YOUR_CLIENT_ID',
      client_secret: 'YOUR_CLIENT_SECRET'
    })
  });
  
  return response.json();
}
```

### 4.2 存储

```javascript
// 安全存储
// 1. Access Token: 内存
// 2. Refresh Token: HttpOnly Cookie 或安全存储
```

## 五、安全最佳实践

### 5.1 Token 安全

```javascript
// 1. 使用 HTTPS
// 2. 设置合理过期时间
// 3. 使用 Refresh Token 机制
// 4. 验证 Token 时检查权限
```

### 5.2 前后端分离

```javascript
// 前端
const response = await fetch('/api/user', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

// 后端验证
app.get('/api/user', verifyToken, (req, res) => {
  res.json({ user: req.user });
});
```

## 六、总结

OAuth 2.0 与 JWT 核心要点：

1. **OAuth 2.0**：授权框架
2. **授权码模式**：最安全
3. **JWT**：Token 格式
4. **Refresh Token**：续期
5. **安全**：HTTPS + 合理过期

掌握这些，认证授权 so easy！

---

**推荐阅读**：
- [OAuth 2.0 官方文档](https://oauth.net/2/)
- [JWT 官方文档](https://jwt.io/)

**如果对你有帮助，欢迎点赞收藏！**
