# OAuth 2.0 完全指南：第三方授权与最佳实践

> 深入讲解 OAuth 2.0 授权机制，包括授权码模式、客户端凭证模式、PKCE 流程，以及实际项目中的安全实现和常见漏洞防护。

## 一、OAuth 2.0 基础

### 1.1 什么是 OAuth 2.0

开放授权标准：

```
┌─────────────────────────────────────────────────────────────┐
│                    OAuth 2.0 流程                            │
│                                                              │
│  用户 ─────▶ 授权 ─────▶ 授权服务器 ──▶ 返回令牌           │
│                     │                                        │
│                     ▼                                        │
│  应用 ──────────────────────────────▶ 资源服务器            │
│                    (使用令牌访问资源)                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Resource Owner | 资源所有者（用户） |
| Client | 客户端应用 |
| Authorization Server | 授权服务器 |
| Resource Server | 资源服务器 |
| Access Token | 访问令牌 |

## 二、授权模式

### 2.1 授权码模式

```
┌─────────────────────────────────────────────────────────────┐
│                 授权码模式（最安全）                          │
│                                                              │
│  1. 用户 ──▶ 授权请求 ──▶ 授权服务器                       │
│                                                              │
│  2. 用户登录并授权                                          │
│                                                              │
│  3. 授权服务器 ──▶ 重定向 ──▶ 应用                         │
│     (携带授权码)                                            │
│                                                              │
│  4. 应用 ──▶ 用授权码换令牌 ──▶ 授权服务器                │
│                                                              │
│  5. 授权服务器 ──▶ 返回令牌 ──▶ 应用                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 请求示例

```http
# 1. 授权请求
GET /authorize?
  response_type=code&
  client_id=myapp&
  redirect_uri=https://myapp.com/callback&
  scope=read:user&
  state=xyz123
HTTP/1.1

# 2. 授权服务器返回
HTTP/1.1 302 Found
Location: https://myapp.com/callback?code=SplxlOBeZQQYbYS6WxSbIA&state=xyz123

# 3. 换令牌请求
POST /token HTTP/1.1
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=SplxlOBeZQQYbYS6WxSbIA&
redirect_uri=https://myapp.com/callback&
client_id=myapp&
client_secret=mysecret

# 4. 返回令牌
HTTP/1.1 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 2.3 隐式模式（不推荐）

```http
# 直接返回令牌（不安全）
GET /authorize?
  response_type=token&
  client_id=myapp&
  redirect_uri=https://myapp.com/callback&
  scope=read:user
HTTP/1.1

# 返回
HTTP/1.1 302 Found
Location: https://myapp.com/callback#access_token=eyJ...&token_type=Bearer
```

### 2.4 客户端凭证模式

```http
# 适用于服务端应用
POST /token HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)

grant_type=client_credentials&
scope=read:users
```

## 三、PKCE 流程

### 3.1 为什么需要 PKCE

防止授权码被拦截：

```
┌─────────────────────────────────────────────────────────────┐
│                      PKCE 流程                              │
│                                                              │
│  1. 生成 code_verifier (随机字符串)                        │
│  2. 生成 code_challenge (hash of verifier)                 │
│  3. 授权请求携带 code_challenge                            │
│  4. 换令牌时提供 code_verifier                            │
│  5. 服务器验证                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 实现

```javascript
// 1. 生成 code_verifier
function generateCodeVerifier() {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return base64UrlEncode(array)
}

// 2. 生成 code_challenge
async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder()
  const data = encoder.encode(verifier)
  const digest = await crypto.subtle.digest('SHA-256', data)
  return base64UrlEncode(new Uint8Array(digest))
}

// 3. 授权请求
const verifier = generateCodeVerifier()
const challenge = await generateCodeChallenge(verifier)

const authUrl = new URL('https://auth.example.com/authorize')
authUrl.searchParams.set('response_type', 'code')
authUrl.searchParams.set('client_id', 'myapp')
authUrl.searchParams.set('redirect_uri', 'https://myapp.com/callback')
authUrl.searchParams.set('code_challenge', challenge)
authUrl.searchParams.set('code_challenge_method', 'S256')
authUrl.searchParams.set('state', generateState())

// 保存 verifier（后续使用）
sessionStorage.setItem('code_verifier', verifier)
```

## 四、令牌管理

### 4.1 刷新令牌

```http
# 刷新请求
POST /token HTTP/1.1
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=eyJhbGciOiJIUzI1NiIs...

# 返回新令牌
HTTP/1.1 200 OK
{
  "access_token": "new_access_token",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 4.2 令牌验证

```javascript
// 验证令牌
const response = await fetch('https://api.example.com/user', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})

// 或者使用 introspection 端点
POST /introspect HTTP/1.1
Content-Type: application/x-www-form-urlencoded

token=eyJhbGciOiJIUzI1NiIs...
```

## 五、安全最佳实践

### 5.1 必做事项

```javascript
// 1. 使用 HTTPS
// 所有通信必须使用 HTTPS

// 2. 验证 redirect_uri
const validRedirectUris = [
  'https://myapp.com/callback',
  'https://myapp.example.com/callback'
]

if (!validRedirectUris.includes redirectUri) {
  throw new Error('Invalid redirect_uri')
}

// 3. 验证 state
const state = generateRandomState()
sessionStorage.setItem('oauth_state', state)

// 4. 使用 PKCE
// 始终使用授权码 + PKCE
```

### 5.2 常见漏洞

| 漏洞 | 防护 |
|------|------|
| 授权码重放 | 一次性使用 + 过期时间 |
| redirect_uri 劫持 | 白名单验证 |
| CSRF | state 参数 |
| Token 泄露 | HTTPS + 安全存储 |

## 六、实战案例

### 6.1 GitHub 登录

```javascript
// 1. 跳转到 GitHub 授权
const GITHUB_CLIENT_ID = 'your_client_id'
const REDIRECT_URI = 'https://yourapp.com/auth/github/callback'

const authUrl = `https://github.com/login/oauth/authorize?` +
  `client_id=${GITHUB_CLIENT_ID}&` +
  `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
  `scope=read:user&` +
  `state=${generateState()}`

window.location.href = authUrl

// 2. 处理回调
const urlParams = new URLSearchParams(window.location.search)
const code = urlParams.get('code')

// 3. 用 code 换 token（后端完成）
const tokenResponse = await fetch('/api/auth/github', {
  method: 'POST',
  body: JSON.stringify({ code })
})

const { accessToken } = await tokenResponse.json()

// 4. 获取用户信息
const userResponse = await fetch('https://api.github.com/user', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})
```

### 6.2 Google 登录

```javascript
// 使用 Google Identity Services
google.accounts.oauth2.initTokenClient({
  client_id: 'your_client_id',
  scope: 'openid profile email',
  callback: (response) => {
    if (response.access_token) {
      // 获取用户信息
      fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
        headers: { 'Authorization': `Bearer ${response.access_token}` }
      })
    }
  }
})
```

## 七、总结

OAuth 2.0 核心要点：

1. **授权码模式**：最安全
2. **PKCE**：防止拦截
3. **state**：防 CSRF
4. **redirect_uri**：白名单
5. **刷新令牌**：有效期管理
6. **HTTPS**：必须使用

掌握这些，第三方登录 so easy！

---

**推荐阅读**：
- [OAuth 2.0 官方文档](https://oauth.net/2/)
- [RFC 6749](https://tools.ietf.org/html/rfc6749)

**如果对你有帮助，欢迎点赞收藏！**
