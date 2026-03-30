# JWT 完全指南：JSON Web Token 实战与安全最佳实践

> 深入讲解 JWT 的结构、签名算法、实际应用场景，以及前后端分离项目中的安全最佳实践。

## 一、JWT 简介

### 1.1 什么是 JWT

JWT（JSON Web Token）是跨域认证的标准：

```javascript
// JWT 示例
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### 1.2 JWT 结构

```
Header.Payload.Signature

xxxxx.yyyyy.zzzzz
```

| 部分 | 说明 |
|------|------|
| Header | 算法和类型 |
| Payload | 载荷数据 |
| Signature | 签名 |

## 二、Header 和 Payload

### 2.1 Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### 2.2 Payload

```json
{
  "sub": "1234567890",
  "name": "张三",
  "role": "admin",
  "iat": 1516239022,
  "exp": 1516242622
}
```

### 2.3 标准声明

| 声明 | 说明 |
|------|------|
| iss | 签发者 |
| sub | 主题 |
| aud | 受众 |
| exp | 过期时间 |
| iat | 签发时间 |

## 三、签名算法

### 3.1 HMAC

```javascript
// 生成 JWT
const jwt = require('jsonwebtoken');

const token = jwt.sign(
  { userId: 123 },
  'secret-key',
  { expiresIn: '1h' }
);

// 验证 JWT
const decoded = jwt.verify(token, 'secret-key');
```

### 3.2 RSA

```javascript
// 使用私钥签名
const token = jwt.sign(
  { userId: 123 },
  privateKey,
  { algorithm: 'RS256' }
);

// 使用公钥验证
const decoded = jwt.verify(token, publicKey);
```

## 四、Node.js 实战

### 4.1 生成 Token

```javascript
const jwt = require('jsonwebtoken');

function generateToken(user) {
  const payload = {
    id: user.id,
    username: user.username,
    role: user.role
  };
  
  return jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: '7d'
  });
}
```

### 4.2 验证 Token

```javascript
const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: '未授权' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token 无效' });
  }
};
```

### 4.3 刷新 Token

```javascript
function refreshToken(token) {
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    const newToken = jwt.sign(
      { id: decoded.id },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    return newToken;
  } catch {
    return null;
  }
}
```

## 五、前端应用

### 5.1 存储 Token

```javascript
// localStorage（不推荐，XSS 攻击）
localStorage.setItem('token', token);

// HttpOnly Cookie（推荐）
// 服务器设置 Set-Cookie: token=xxx; HttpOnly; Secure
```

### 5.2 请求头

```javascript
const fetchWithAuth = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
};
```

## 六、安全最佳实践

### 6.1 重要原则

- 使用强密钥（至少 256 位）
- 设置合理过期时间
- 使用 HTTPS
- 不存储敏感信息

### 6.2 过期时间

```javascript
// 短期访问 Token
const accessToken = jwt.sign(payload, secret, { expiresIn: '15m' });

// 长期刷新 Token
const refreshToken = jwt.sign(payload, secret, { expiresIn: '7d' });
```

### 6.3 密钥管理

```javascript
// 环境变量
const JWT_SECRET = process.env.JWT_SECRET || 'change-this-in-production';
```

## 七、实战案例

### 7.1 完整登录流程

```javascript
// 登录
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  const user = await User.findOne({ username });
  if (!user || !await bcrypt.compare(password, user.password)) {
    return res.status(401).json({ error: '用户名或密码错误' });
  }
  
  const token = jwt.sign(
    { id: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '1h' }
  );
  
  const refreshToken = jwt.sign(
    { id: user.id },
    process.env.REFRESH_SECRET,
    { expiresIn: '7d' }
  );
  
  res.json({ token, refreshToken });
});
```

### 7.2 中间件保护

```javascript
const auth = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: '需要登录' });
  }
  
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ error: 'Token 无效' });
  }
};

// 保护路由
app.get('/profile', auth, (req, res) => {
  res.json(req.user);
});
```

## 八、总结

JWT 核心要点：

1. **结构**：Header.Payload.Signature
2. **签名**：HS256、RS256
3. **生成**：jwt.sign()
4. **验证**：jwt.verify()
5. **安全**：HTTPS、强密钥、合理过期
6. **存储**：HttpOnly Cookie

掌握这些，认证系统不再难！

---

**推荐阅读**：
- [JWT.io](https://jwt.io/)
- [RFC 7519](https://tools.ietf.org/html/rfc7519)

**如果对你有帮助，欢迎点赞收藏！**
