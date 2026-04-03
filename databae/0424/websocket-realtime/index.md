# WebSocket 实时通信完全指南：从基础到实战应用

WebSocket 是一种在单个 TCP 连接上进行全双工通信的协议。本文将带你全面掌握 WebSocket 的应用开发。

## 一、WebSocket 基础

### 1. WebSocket 协议特点

```
HTTP (请求-响应模式):
客户端 → 请求 → 服务器
客户端 ← 响应 ← 服务器
(每次通信需要建立新连接)

WebSocket (全双工):
客户端 ←→ 服务器
(持久连接，双向实时通信)
```

- **全双工**: 客户端和服务器可以同时发送数据
- **持久连接**: 连接建立后持续保持
- **低延迟**: 不需要重复建立连接
- **实时**: 数据可以即时推送

### 2. 浏览器端 API

```javascript
// 创建 WebSocket 连接
const ws = new WebSocket('ws://localhost:8080/ws');

// 连接建立
ws.onopen = function(event) {
  console.log('WebSocket connected!');
  ws.send('Hello Server!');
};

// 接收消息
ws.onmessage = function(event) {
  console.log('Received:', event.data);
};

// 连接关闭
ws.onclose = function(event) {
  console.log('WebSocket closed:', event.code, event.reason);
};

// 错误处理
ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};

// 发送消息
document.getElementById('sendBtn').addEventListener('click', () => {
  const message = document.getElementById('messageInput').value;
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(message);
  }
});

// 优雅关闭
function closeWebSocket() {
  if (ws.readyState === WebSocket.OPEN) {
    ws.close(1000, 'Normal closure');
  }
}
```

### 3. 连接状态

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

switch (ws.readyState) {
  case WebSocket.CONNECTING: // 0
    console.log('Connecting...');
    break;
  case WebSocket.OPEN: // 1
    console.log('Open and ready to communicate');
    break;
  case WebSocket.CLOSING: // 2
    console.log('Connection is closing');
    break;
  case WebSocket.CLOSED: // 3
    console.log('Connection is closed');
    break;
}
```

## 二、Node.js WebSocket 服务器

### 1. 使用 ws 库

```bash
npm install ws
```

```javascript
// server.js
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

console.log('WebSocket server running on port 8080');

wss.on('connection', function connection(ws) {
  console.log('New client connected');
  
  ws.on('message', function message(data) {
    console.log('Received:', data.toString());
    
    // 广播给所有客户端
    wss.clients.forEach(function each(client) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data.toString());
      }
    });
  });
  
  ws.on('close', function close() {
    console.log('Client disconnected');
  });
  
  ws.on('error', function error(err) {
    console.error('WebSocket error:', err);
  });
  
  // 发送欢迎消息
  ws.send('Welcome to WebSocket server!');
});
```

### 2. 简单聊天室

```html
<!DOCTYPE html>
<html>
<head>
  <title>WebSocket Chat</title>
  <style>
    #messages { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }
    .message { margin-bottom: 5px; }
    .system { color: #999; font-style: italic; }
  </style>
</head>
<body>
  <div id="messages"></div>
  <input type="text" id="username" placeholder="Your name">
  <input type="text" id="messageInput" placeholder="Enter message">
  <button id="sendBtn">Send</button>

  <script>
    const ws = new WebSocket('ws://localhost:8080');
    const messagesDiv = document.getElementById('messages');
    const usernameInput = document.getElementById('username');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');

    function addMessage(text, isSystem = false) {
      const div = document.createElement('div');
      div.className = isSystem ? 'message system' : 'message';
      div.textContent = text;
      messagesDiv.appendChild(div);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    ws.onopen = () => {
      addMessage('Connected to chat', true);
    };

    ws.onmessage = (event) => {
      addMessage(event.data);
    };

    ws.onclose = () => {
      addMessage('Disconnected from chat', true);
    };

    function sendMessage() {
      const username = usernameInput.value.trim() || 'Anonymous';
      const message = messageInput.value.trim();
      if (message && ws.readyState === WebSocket.OPEN) {
        ws.send(`${username}: ${message}`);
        messageInput.value = '';
      }
    }

    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
  </script>
</body>
</html>
```

### 3. 使用 Socket.io（更高级的库）

```bash
npm install socket.io express
```

```javascript
// server.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// 房间管理
const rooms = new Map();

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  // 加入房间
  socket.on('join-room', (roomId, username) => {
    socket.join(roomId);
    socket.data.username = username;
    socket.data.roomId = roomId;
    
    if (!rooms.has(roomId)) {
      rooms.set(roomId, new Set());
    }
    rooms.get(roomId).add(socket.id);
    
    io.to(roomId).emit('user-joined', {
      userId: socket.id,
      username: username,
      users: Array.from(rooms.get(roomId)).map(id => ({
        id,
        username: io.sockets.sockets.get(id)?.data?.username
      }))
    });
    
    console.log(`${username} joined room ${roomId}`);
  });

  // 发送消息
  socket.on('send-message', (message) => {
    const roomId = socket.data.roomId;
    if (roomId) {
      io.to(roomId).emit('new-message', {
        userId: socket.id,
        username: socket.data.username,
        text: message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // 发送信令（用于 WebRTC）
  socket.on('signal', (data) => {
    io.to(data.targetId).emit('signal', {
      from: socket.id,
      signal: data.signal
    });
  });

  // 断开连接
  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
    const roomId = socket.data.roomId;
    if (roomId && rooms.has(roomId)) {
      rooms.get(roomId).delete(socket.id);
      io.to(roomId).emit('user-left', {
        userId: socket.id,
        username: socket.data.username
      });
      if (rooms.get(roomId).size === 0) {
        rooms.delete(roomId);
      }
    }
  });
});

server.listen(3001, () => {
  console.log('Socket.io server running on port 3001');
});
```

```javascript
// client.js
import { io } from 'socket.io-client';

const socket = io('http://localhost:3001');

socket.on('connect', () => {
  console.log('Connected to server');
});

// 加入房间
function joinRoom(roomId, username) {
  socket.emit('join-room', roomId, username);
}

// 发送消息
function sendMessage(text) {
  socket.emit('send-message', text);
}

// 监听事件
socket.on('user-joined', (data) => {
  console.log('User joined:', data);
});

socket.on('user-left', (data) => {
  console.log('User left:', data);
});

socket.on('new-message', (message) => {
  console.log('New message:', message);
});

socket.on('signal', (data) => {
  console.log('Received signal:', data);
});
```

## 三、实战项目：实时协作白板

### 1. 服务器端

```javascript
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" }
});

const whiteboards = new Map();

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('join-whiteboard', (boardId) => {
    socket.join(boardId);
    socket.data.boardId = boardId;
    
    if (!whiteboards.has(boardId)) {
      whiteboards.set(boardId, {
        strokes: [],
        users: new Set()
      });
    }
    
    const board = whiteboards.get(boardId);
    board.users.add(socket.id);
    
    socket.emit('init-board', {
      strokes: board.strokes,
      userCount: board.users.size
    });
    
    io.to(boardId).emit('user-count', board.users.size);
  });

  socket.on('draw', (stroke) => {
    const boardId = socket.data.boardId;
    if (boardId && whiteboards.has(boardId)) {
      whiteboards.get(boardId).strokes.push(stroke);
      socket.to(boardId).emit('draw', stroke);
    }
  });

  socket.on('clear-board', () => {
    const boardId = socket.data.boardId;
    if (boardId && whiteboards.has(boardId)) {
      whiteboards.get(boardId).strokes = [];
      io.to(boardId).emit('clear-board');
    }
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
    const boardId = socket.data.boardId;
    if (boardId && whiteboards.has(boardId)) {
      const board = whiteboards.get(boardId);
      board.users.delete(socket.id);
      io.to(boardId).emit('user-count', board.users.size);
      if (board.users.size === 0) {
        whiteboards.delete(boardId);
      }
    }
  });
});

server.listen(3001, () => {
  console.log('Whiteboard server on port 3001');
});
```

### 2. 客户端

```html
<!DOCTYPE html>
<html>
<head>
  <title>Collaborative Whiteboard</title>
  <style>
    #canvas { border: 1px solid #000; cursor: crosshair; }
    .toolbar { margin-bottom: 10px; }
  </style>
</head>
<body>
  <div class="toolbar">
    <input type="color" id="colorPicker" value="#000000">
    <input type="range" id="brushSize" min="1" max="50" value="5">
    <button id="clearBtn">Clear</button>
    <span id="userCount">Users: 0</span>
  </div>
  <canvas id="canvas" width="800" height="600"></canvas>

  <script src="/socket.io/socket.io.js"></script>
  <script>
    const socket = io();
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const colorPicker = document.getElementById('colorPicker');
    const brushSize = document.getElementById('brushSize');
    const clearBtn = document.getElementById('clearBtn');
    const userCountSpan = document.getElementById('userCount');

    let isDrawing = false;
    let currentStroke = [];

    const boardId = 'demo-board';
    const username = 'User-' + Math.random().toString(36).substr(2, 5);

    socket.emit('join-whiteboard', boardId, username);

    socket.on('init-board', (data) => {
      data.strokes.forEach(drawStroke);
      userCountSpan.textContent = 'Users: ' + data.userCount;
    });

    socket.on('draw', (stroke) => {
      drawStroke(stroke);
    });

    socket.on('clear-board', () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    });

    socket.on('user-count', (count) => {
      userCountSpan.textContent = 'Users: ' + count;
    });

    function drawStroke(stroke) {
      if (stroke.points.length < 2) return;
      
      ctx.beginPath();
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.size;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      
      ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
      for (let i = 1; i < stroke.points.length; i++) {
        ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
      }
      ctx.stroke();
    }

    function getPosition(e) {
      const rect = canvas.getBoundingClientRect();
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    }

    canvas.addEventListener('mousedown', (e) => {
      isDrawing = true;
      currentStroke = {
        color: colorPicker.value,
        size: parseInt(brushSize.value),
        points: [getPosition(e)]
      };
    });

    canvas.addEventListener('mousemove', (e) => {
      if (!isDrawing) return;
      currentStroke.points.push(getPosition(e));
      drawStroke(currentStroke);
    });

    canvas.addEventListener('mouseup', () => {
      if (isDrawing && currentStroke.points.length > 1) {
        socket.emit('draw', currentStroke);
      }
      isDrawing = false;
      currentStroke = [];
    });

    canvas.addEventListener('mouseleave', () => {
      if (isDrawing && currentStroke.points.length > 1) {
        socket.emit('draw', currentStroke);
      }
      isDrawing = false;
      currentStroke = [];
    });

    clearBtn.addEventListener('click', () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      socket.emit('clear-board');
    });
  </script>
</body>
</html>
```

## 四、WebSocket 安全

### 1. 使用 WSS（WebSocket Secure）

```javascript
const https = require('https');
const fs = require('fs');
const WebSocket = require('ws');

const server = https.createServer({
  cert: fs.readFileSync('cert.pem'),
  key: fs.readFileSync('key.pem')
});

const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('Secure WebSocket connection');
});

server.listen(8443);
```

```javascript
// 客户端使用 wss://
const ws = new WebSocket('wss://localhost:8443');
```

### 2. 认证

```javascript
const WebSocket = require('ws');
const jwt = require('jsonwebtoken');

const wss = new WebSocket.Server({ noServer: true });

wss.on('connection', (ws, req, user) => {
  ws.user = user;
  console.log('Authenticated user:', user.username);
});

const server = http.createServer();
server.on('upgrade', (request, socket, head) => {
  const token = request.headers['sec-websocket-protocol'];
  
  try {
    const user = jwt.verify(token, 'your-secret-key');
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request, user);
    });
  } catch (error) {
    socket.destroy();
  }
});

server.listen(8080);
```

## 五、性能优化

### 1. 二进制数据

```javascript
// 发送二进制数据
const buffer = new ArrayBuffer(4);
const view = new Int32Array(buffer);
view[0] = 12345;

ws.send(buffer);

// 接收二进制数据
ws.binaryType = 'arraybuffer';
ws.onmessage = (event) => {
  const buffer = event.data;
  const view = new Int32Array(buffer);
  console.log(view[0]);
};
```

### 2. 心跳检测

```javascript
// 服务器端
wss.on('connection', (ws) => {
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.ping();
    }
  }, 30000);

  ws.on('pong', () => {
    // 客户端响应
  });

  ws.on('close', () => {
    clearInterval(interval);
  });
});

// 客户端
ws.on('ping', () => {
  ws.pong();
});
```

## 六、最佳实践

1. 使用 WSS 而非 WS（安全连接）
2. 实现认证机制
3. 处理重连和断线重连
4. 消息序列化（JSON/Protocol Buffers）
5. 心跳检测保持连接
6. 限制消息大小
7. 实现房间/频道管理
8. 错误处理和日志
9. 性能监控
10. 水平扩展

## 七、总结

WebSocket 核心要点：
- 理解 WebSocket 协议和 API
- 使用 ws 或 Socket.io 构建服务器
- 实现实时聊天和协作应用
- 注意安全性（WSS、认证）
- 性能优化（二进制、心跳）
- 遵循最佳实践

开始用 WebSocket 构建你的实时应用吧！
