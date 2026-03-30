# WebSocket 与 Socket.io 完全指南：实时通信实战

> 深入讲解 WebSocket 和 Socket.io，包括连接建立、事件处理、房间管理，以及实际项目中的实时聊天、推送通知等场景实现。

## 一、WebSocket 基础

### 1.1 什么是 WebSocket

全双工通信协议：

```
HTTP: 请求 → 响应 → 关闭
WebSocket: 建立连接 → 双向通信 → 关闭
```

### 1.2 原生 WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8080');

ws.onopen = () => {
  console.log('连接建立');
  ws.send('Hello');
};

ws.onmessage = (event) => {
  console.log('收到消息:', event.data);
};

ws.onerror = (error) => {
  console.error('错误:', error);
};

ws.onclose = () => {
  console.log('连接关闭');
};
```

### 1.3 服务端

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('客户端连接');
  
  ws.on('message', (message) => {
    console.log('收到:', message);
    ws.send('收到: ' + message);
  });
  
  ws.send('欢迎连接');
});
```

## 二、Socket.io

### 2.1 安装

```bash
npm install socket.io socket.io-client
```

### 2.2 服务端

```javascript
const { Server } = require('socket.io');

const io = new Server(3000, {
  cors: {
    origin: '*'
  }
});

io.on('connection', (socket) => {
  console.log('用户连接:', socket.id);
  
  socket.on('message', (data) => {
    io.emit('message', data);
  });
  
  socket.on('disconnect', () => {
    console.log('用户断开');
  });
});
```

### 2.3 客户端

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:3000');

socket.on('connect', () => {
  console.log('已连接');
});

socket.on('message', (data) => {
  console.log('收到:', data);
});

socket.emit('message', 'Hello');
```

## 三、事件处理

### 3.1 自定义事件

```javascript
// 发送
socket.emit('chat message', 'Hello');

// 接收
socket.on('chat message', (msg) => {
  console.log(msg);
});
```

### 3.2 广播

```javascript
// 发送给所有人
io.emit('broadcast', 'Hello');

// 发送给除自己外的所有人
socket.broadcast.emit('others', 'Hello');

// 发送给房间
io.to('room1').emit('room message', 'Hello');
```

## 四、房间管理

### 4.1 加入房间

```javascript
// 客户端
socket.emit('join', 'room1');

// 服务端
socket.on('join', (room) => {
  socket.join(room);
});
```

### 4.2 离开房间

```javascript
socket.on('leave', (room) => {
  socket.leave(room);
});
```

### 4.3 房间消息

```javascript
io.to('room1').emit('message', 'Room1 消息');
io.to('room2').emit('message', 'Room2 消息');
```

## 五、实战案例

### 5.1 实时聊天

```javascript
// 服务端
io.on('connection', (socket) => {
  socket.on('chat', (data) => {
    io.emit('chat', {
      id: socket.id,
      message: data.message,
      time: new Date()
    });
  });
});

// 客户端
socket.on('chat', (data) => {
  addMessage(data);
});

function sendMessage(message) {
  socket.emit('chat', { message });
}
```

### 5.2 在线状态

```javascript
io.on('connection', (socket) => {
  socket.on('online', (userId) => {
    socket.userId = userId;
    io.emit('user online', userId);
  });
  
  socket.on('disconnect', () => {
    io.emit('user offline', socket.userId);
  });
});
```

## 六、总结

WebSocket/Socket.io 核心要点：

1. **WebSocket**：原生全双工
2. **Socket.io**：封装增强
3. **事件**：emit/on
4. **广播**：broadcast
5. **房间**：join/leave

掌握这些，实时通信 so easy！

---

**推荐阅读**：
- [Socket.io 官方文档](https://socket.io/docs/)

**如果对你有帮助，欢迎点赞收藏！**
