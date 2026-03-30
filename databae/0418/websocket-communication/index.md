# WebSocket 完全指南：实时通信实战

> 深入讲解 WebSocket 协议，包括连接建立、心跳机制、消息类型，以及 Socket.io、WS 库的实际应用和性能优化。

## 一、WebSocket 基础

### 1.1 什么是 WebSocket

全双工通信协议：

```
┌─────────────────────────────────────────────────────────────┐
│              HTTP vs WebSocket                              │
│                                                              │
│  HTTP                                                        │
│  Client ──▶ Request ──▶ Server                             │
│  Client ◀── Response ◀── Server                            │
│  (半双工，每次请求需重新建立连接)                           │
│                                                              │
│  WebSocket                                                  │
│  Client ═══════════════════════ Server                       │
│  (全双工，一次连接，双向通信)                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 连接建立

```javascript
// 客户端
const ws = new WebSocket('ws://example.com/ws')

ws.onopen = () => {
  console.log('Connected')
}

ws.onmessage = (event) => {
  console.log('Received:', event.data)
}

ws.onclose = () => {
  console.log('Disconnected')
}

// 发送消息
ws.send(JSON.stringify({ type: 'hello' }))
```

## 二、握手过程

### 2.1 HTTP 升级

```http
# 请求
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

# 响应
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 2.2 Node.js 实现

```javascript
const http = require('http')
const WebSocket = require('ws')

const server = http.createServer()
const wss = new WebSocket.Server({ server })

wss.on('connection', (ws, req) => {
  console.log('Client connected')
  
  ws.on('message', (message) => {
    console.log('Received:', message)
    ws.send('Echo: ' + message)
  })
  
  ws.on('close', () => {
    console.log('Client disconnected')
  })
})

server.listen(8080, () => {
  console.log('WebSocket server running on port 8080')
})
```

## 三、心跳机制

### 3.1 心跳原理

```
┌─────────────────────────────────────────────────────────────┐
│                    心跳机制                                  │
│                                                              │
│  Client ──▶ ping ──▶ Server                                │
│  Client ◀── pong ◀── Server                                │
│                                                              │
│  作用:                                                      │
│  1. 检测连接是否存活                                        │
│  2. 保持连接活跃（防止代理关闭）                            │
│  3. 及时发现断连                                            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 实现

```javascript
// 心跳定时器
const HEARTBEAT_INTERVAL = 30000

let heartbeatTimer = null

ws.on('open', () => {
  heartbeatTimer = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }, HEARTBEAT_INTERVAL)
})

ws.on('message', (data) => {
  const msg = JSON.parse(data)
  if (msg.type === 'pong') {
    console.log('Heartbeat received')
  }
})

ws.on('close', () => {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
  }
})
```

## 四、消息类型

### 4.1 消息格式

```json
// 文本消息
{ "type": "message", "content": "Hello", "from": "user1" }

// 事件消息
{ "event": "user_joined", "data": { "userId": "123" } }

// 心跳
{ "type": "ping" }
{ "type": "pong" }

// 错误
{ "type": "error", "code": 4001, "message": "Invalid token" }
```

### 4.2 事件驱动

```javascript
// 服务器端
wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    const msg = JSON.parse(data)
    
    switch (msg.type) {
      case 'chat':
        broadcast({ type: 'chat', message: msg.message })
        break
      case 'join':
        ws.room = msg.room
        joinRoom(ws, msg.room)
        break
      case 'leave':
        leaveRoom(ws, ws.room)
        break
    }
  })
})

// 广播
function broadcast(message) {
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message))
    }
  })
}
```

## 五、Socket.io

### 5.1 基础使用

```javascript
// 服务端
const io = require('socket.io')(3000)

io.on('connection', (socket) => {
  console.log('User connected:', socket.id)
  
  socket.on('message', (data) => {
    io.emit('message', data)
  })
  
  socket.on('disconnect', () => {
    console.log('User disconnected')
  })
})

// 客户端
const socket = io('http://localhost:3000')

socket.on('connect', () => {
  console.log('Connected')
})

socket.on('message', (data) => {
  console.log('Received:', data)
})

socket.emit('message', 'Hello')
```

### 5.2 房间管理

```javascript
// 加入房间
socket.join('room1')

// 向房间发送
io.to('room1').emit('message', 'Hello room1')

// 离开房间
socket.leave('room1')

// 私聊
socket.to(socketId).emit('private', 'Secret message')
```

## 六、重连机制

### 6.1 自动重连

```javascript
// Socket.io 自动重连配置
const socket = io('http://localhost:3000', {
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000
})

socket.on('reconnect', (attempt) => {
  console.log('Reconnected after', attempt, 'attempts')
})

socket.on('reconnect_failed', () => {
  console.log('Reconnection failed')
})
```

### 6.2 手动重连

```javascript
// 原生 WebSocket 重连
class ReconnectingWebSocket {
  constructor(url) {
    this.url = url
    this.connect()
  }
  
  connect() {
    this.ws = new WebSocket(this.url)
    
    this.ws.onclose = () => {
      console.log('Disconnected, reconnecting...')
      setTimeout(() => this.connect(), 1000)
    }
  }
  
  send(data) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data)
    }
  }
}
```

## 七、实战案例

### 7.1 聊天应用

```javascript
// 服务端
const io = require('socket.io')(3000)

const users = new Map()
const rooms = new Map()

io.on('connection', (socket) => {
  // 用户登录
  socket.on('login', ({ username }) => {
    users.set(socket.id, { username, room: 'lobby' })
    socket.join('lobby')
    io.to('lobby').emit('system', `${username} joined`)
  })
  
  // 发送消息
  socket.on('message', ({ content }) => {
    const user = users.get(socket.id)
    if (user) {
      io.to(user.room).emit('message', {
        username: user.username,
        content,
        time: new Date().toISOString()
      })
    }
  })
  
  // 切换房间
  socket.on('joinRoom', ({ room }) => {
    const user = users.get(socket.id)
    if (user) {
      socket.leave(user.room)
      user.room = room
      socket.join(room)
      io.to(room).emit('system', `${user.username} joined`)
    }
  })
})
```

### 7.2 在线状态

```javascript
// 服务端
io.on('connection', (socket) => {
  // 用户上线
  socket.on('online', ({ userId }) => {
    // 更新 Redis
    redis.set(`online:${userId}`, socket.id)
    // 广播给好友
    broadcastFriends(userId, { type: 'online', userId })
  })
  
  // 心跳保活
  socket.on('heartbeat', () => {
    // 更新最后活跃时间
    redis.set(`lastActive:${socket.id}`, Date.now())
  })
  
  // 离线
  socket.on('disconnect', () => {
    redis.del(`online:${socket.id}`)
  })
})
```

## 八、总结

WebSocket 核心要点：

1. **全双工**：双向通信
2. **握手**：HTTP 升级
3. **心跳**：保持连接
4. **消息**：JSON 格式
5. **Socket.io**：封装库
6. **重连**：自动重连
7. **房间**：群组管理

掌握这些，实时通信 so easy！

---

**推荐阅读**：
- [WebSocket 协议](https://tools.ietf.org/html/rfc6455)
- [Socket.io 文档](https://socket.io/docs/)

**如果对你有帮助，欢迎点赞收藏！**
