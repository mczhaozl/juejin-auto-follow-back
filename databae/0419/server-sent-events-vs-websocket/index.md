# Server-Sent Events vs WebSocket：深度对比与实战选择

> 一句话摘要：全面对比 Server-Sent Events (SSE) 和 WebSocket 两种实时通信技术，从协议原理、性能特点、适用场景出发，帮助你在项目中做出正确的技术选型。

## 一、引言

### 1.1 实时通信的需求

现代 Web 应用对实时数据交换的需求越来越普遍：

- **股票行情**：毫秒级的价格更新
- **聊天应用**：即时消息推送
- **在线协作**：多人实时编辑
- **监控系统**：实时状态更新
- **进度通知**：长任务进度反馈

### 1.2 两种主流方案

在浏览器与服务器之间实现实时通信，主要有两种技术：

| 特性 | Server-Sent Events (SSE) | WebSocket |
|------|-------------------------|----------|
| 方向 | 单向（服务器→客户端） | 双向 |
| 协议 | HTTP/HTTPS | 独立协议 (ws:// / wss://) |
| 兼容性 | 现代浏览器 | 所有现代浏览器 |
| 重连 | 自动重连 | 需手动实现 |
| 数据格式 | 文本为主 | 文本或二进制 |
| NAT 穿透 | 天然支持 | 可能有问题 |

### 1.3 本文目标

1. 理解两种技术的底层协议
2. 掌握各自的优缺点
3. 学习实际应用场景
4. 做出正确的技术选型

## 二、Server-Sent Events 详解

### 2.1 协议原理

SSE 是基于 HTTP 的服务器推送技术：

```
┌─────────────────────────────────────────────────────────┐
│                     SSE 连接建立                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   客户端 ──→ HTTP 请求（带 Accept: text/event-stream）    │
│              ↓                                            │
│   服务器 ──→ HTTP 响应（200 OK, Content-Type: text/event │
│              ↓                           -stream）       │
│   服务器 ──→ 数据流: data: {"type":"price","value":100}  │
│              ↓                                            │
│   服务器 ──→ 数据流: data: {"type":"price","value":101}  │
│              ↓                                            │
│   ... (持续推送)                                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 服务器端实现

#### Node.js 实现

```javascript
// sse-server.js
const http = require('http');

const server = http.createServer((req, res) => {
    if (req.url === '/events') {
        // 设置 SSE 响应头
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        });

        // 每秒发送一次数据
        const intervalId = setInterval(() => {
            const data = {
                timestamp: Date.now(),
                message: `服务器时间: ${new Date().toISOString()}`
            };

            // 格式化 SSE 数据
            res.write(`data: ${JSON.stringify(data)}\n\n`);

            // 检测客户端是否断开
            if (res.destroyed) {
                clearInterval(intervalId);
                console.log('客户端断开连接');
            }
        }, 1000);

        // 客户端断开时清理
        req.on('close', () => {
            clearInterval(intervalId);
            console.log('连接已关闭');
        });

    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

server.listen(3000, () => {
    console.log('SSE 服务器运行在 http://localhost:3000/events');
});
```

#### Express 实现

```javascript
// sse-express.js
const express = require('express');
const app = express();

const clients = new Set();

app.get('/events', (req, res) => {
    // 设置 SSE 头
    res.set({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    });

    // 添加到客户端列表
    clients.add(res);
    console.log(`客户端连接，当前: ${clients.size} 个`);

    // 发送初始消息
    res.write('data: {"type":"connected","count":1}\n\n');

    // 清理
    req.on('close', () => {
        clients.delete(res);
        console.log(`客户端断开，当前: ${clients.size} 个`);
    });
});

// 广播消息给所有客户端
function broadcast(message) {
    for (const client of clients) {
        client.write(`data: ${JSON.stringify(message)}\n\n`);
    }
}

// 示例：定时广播
setInterval(() => {
    broadcast({
        type: 'heartbeat',
        timestamp: Date.now()
    });
}, 30000);

app.listen(3000, () => {
    console.log('Express SSE 服务器运行在 http://localhost:3000');
});
```

#### Python FastAPI 实现

```python
# sse_fastapi.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime

app = FastAPI()

async def event_generator():
    while True:
        # 模拟数据生成
        data = {
            "timestamp": datetime.now().isoformat(),
            "value": round(asyncio.get_event_loop().time() % 100, 2)
        }

        # 格式化 SSE 数据
        yield f"data: {json.dumps(data)}\n\n"

        # 每秒发送一次
        await asyncio.sleep(1)

@app.get("/events")
async def sse_endpoint(request: Request):
    async def generate():
        # 发送初始连接消息
        yield f"data: {json.dumps({'type': 'connected'})}\n\n"

        async for event in event_generator():
            # 检查客户端是否断开
            if await request.is_disconnected():
                break
            yield event

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )
```

### 2.3 客户端实现

#### 原生 JavaScript

```javascript
// sse-client.js
class SSEManager {
    constructor(url) {
        this.url = url;
        this.eventSource = null;
        this.handlers = new Map();
    }

    connect() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        this.eventSource = new EventSource(this.url);

        // 监听所有事件
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.emit('message', data);
            } catch (e) {
                console.error('解析失败:', e);
            }
        };

        // 监听自定义事件
        this.eventSource.addEventListener('price', (event) => {
            const data = JSON.parse(event.data);
            this.emit('price', data);
        });

        this.eventSource.addEventListener('error', (event) => {
            console.error('SSE 错误:', event);
            this.emit('error', event);
        });

        this.eventSource.onopen = () => {
            console.log('SSE 连接已建立');
            this.emit('open');
        };
    }

    on(event, handler) {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, new Set());
        }
        this.handlers.get(event).add(handler);
    }

    emit(event, data) {
        const eventHandlers = this.handlers.get(event);
        if (eventHandlers) {
            eventHandlers.forEach(handler => handler(data));
        }
    }

    close() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }
}

// 使用
const sse = new SSEManager('http://localhost:3000/events');

sse.on('open', () => console.log('已连接'));
sse.on('message', (data) => console.log('收到消息:', data));
sse.on('price', (data) => updatePrice(data));

sse.connect();

// 组件卸载时关闭
window.addEventListener('beforeunload', () => sse.close());
```

#### React Hook

```javascript
// useSSE.js
import { useEffect, useRef, useState } from 'react';

function useSSE(url, options = {}) {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [connected, setConnected] = useState(false);
    const eventSourceRef = useRef(null);

    useEffect(() => {
        if (!url) return;

        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            setConnected(true);
            setError(null);
        };

        eventSource.onmessage = (event) => {
            try {
                const parsed = JSON.parse(event.data);
                setData(parsed);
            } catch (e) {
                console.error('解析失败:', e);
            }
        };

        eventSource.onerror = (err) => {
            console.error('SSE 错误:', err);
            setError(err);
            setConnected(false);

            // 自动重连（EventSource 自带重连机制）
        };

        // 自定义事件
        if (options.event) {
            eventSource.addEventListener(options.event, (event) => {
                try {
                    const parsed = JSON.parse(event.data);
                    setData(parsed);
                } catch (e) {
                    console.error('解析失败:', e);
                }
            });
        }

        return () => {
            eventSource.close();
        };
    }, [url]);

    return { data, error, connected };
}

// 使用
function StockPrice() {
    const { data, connected } = useSSE('http://localhost:3000/events', {
        event: 'price'
    });

    return (
        <div>
            <p>状态: {connected ? '已连接' : '未连接'}</p>
            {data && <p>价格: {data.value}</p>}
        </div>
    );
}
```

### 2.4 SSE 事件格式

```bash
# 标准格式
event: message
data: {"content": "Hello"}

# 多行数据
data: {"line1": "第一行"}
data: {"line2": "第二行"}

# ID 用于断线重连
id: 1
event: update
data: {"value": 100}

id: 2
event: update
data: {"value": 101}

# 重试间隔（毫秒）
retry: 5000

# 完整示例
: 这是注释
event: custom
id: 100
retry: 10000
data: {"message": "Hello SSE"}
data: {"line2": "第二行"}
```

## 三、WebSocket 详解

### 3.1 协议原理

WebSocket 在建立连接前使用 HTTP 握手，然后升级为双向通信：

```
┌─────────────────────────────────────────────────────────┐
│                  WebSocket 握手过程                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   1. 客户端发送 HTTP 请求（包含 Upgrade 头）              │
│   GET /ws HTTP/1.1                                      │
│   Host: localhost:3000                                   │
│   Upgrade: websocket                                     │
│   Connection: Upgrade                                   │
│   Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==           │
│   Sec-WebSocket-Version: 13                             │
│                                                          │
│   2. 服务器响应（101 Switching Protocols）                │
│   HTTP/1.1 101 Switching Protocols                       │
│   Upgrade: websocket                                     │
│   Connection: Upgrade                                   │
│   Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYG3hQbXA==       │
│                                                          │
│   3. 握手完成后，双方使用 WebSocket 帧进行通信            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 3.2 服务器端实现

#### Node.js ws 库

```javascript
// ws-server.js
const { WebSocketServer } = require('ws');

const wss = new WebSocketServer({ port: 3000 });

console.log('WebSocket 服务器运行在 ws://localhost:3000');

wss.on('connection', (ws, req) => {
    const clientIp = req.socket.remoteAddress;
    console.log(`客户端连接: ${clientIp}`);

    // 发送欢迎消息
    ws.send(JSON.stringify({
        type: 'welcome',
        message: '连接成功'
    }));

    // 监听客户端消息
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log('收到消息:', data);

            // 处理不同类型的消息
            switch (data.type) {
                case 'ping':
                    ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
                    break;
                case 'chat':
                    broadcast({
                        type: 'chat',
                        sender: clientIp,
                        message: data.message,
                        timestamp: Date.now()
                    });
                    break;
                default:
                    console.log('未知消息类型:', data.type);
            }
        } catch (e) {
            console.error('消息解析失败:', e);
        }
    });

    // 连接关闭
    ws.on('close', () => {
        console.log(`客户端断开: ${clientIp}`);
    });

    // 错误处理
    ws.on('error', (error) => {
        console.error('WebSocket 错误:', error);
    });
});

// 广播消息给所有客户端
function broadcast(message) {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}

// 定时广播（示例）
setInterval(() => {
    broadcast({
        type: 'heartbeat',
        timestamp: Date.now(),
        clients: wss.clients.size
    });
}, 30000);
```

#### Socket.IO（更高级的封装）

```javascript
// socketio-server.js
const { Server } = require('socket.io');
const http = require('http');

const httpServer = http.createServer();
const io = new Server(httpServer, {
    cors: {
        origin: "*"
    }
});

io.on('connection', (socket) => {
    console.log(`客户端连接: ${socket.id}`);

    // 加入房间
    socket.on('join-room', (roomId) => {
        socket.join(roomId);
        console.log(`客户端 ${socket.id} 加入房间 ${roomId}`);
        socket.to(roomId).emit('user-joined', { socketId: socket.id });
    });

    // 发送消息到房间
    socket.on('room-message', ({ roomId, message }) => {
        io.to(roomId).emit('room-message', {
            from: socket.id,
            message,
            timestamp: Date.now()
        });
    });

    // 离开房间
    socket.on('leave-room', (roomId) => {
        socket.leave(roomId);
        socket.to(roomId).emit('user-left', { socketId: socket.id });
    });

    // 断开连接
    socket.on('disconnect', () => {
        console.log(`客户端断开: ${socket.id}`);
    });
});

httpServer.listen(3000, () => {
    console.log('Socket.IO 服务器运行在 http://localhost:3000');
});
```

#### Python 实现

```python
# ws_python.py
import asyncio
import websockets
import json
from datetime import datetime

async def handle_client(websocket, path):
    client_id = id(websocket)
    print(f"客户端连接: {client_id}")

    try:
        # 发送欢迎消息
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "连接成功"
        }))

        # 监听消息
        async for message in websocket:
            data = json.loads(message)
            print(f"收到消息: {data}")

            if data.get("type") == "ping":
                await websocket.send(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            elif data.get("type") == "chat":
                # 广播消息
                await websocket.send(json.dumps({
                    "type": "chat",
                    "message": data.get("message"),
                    "timestamp": datetime.now().isoformat()
                }))

    except websockets.exceptions.ConnectionClosed:
        print(f"客户端断开: {client_id}")

async def main():
    async with websockets.serve(handle_client, "localhost", 3000):
        print("WebSocket 服务器运行在 ws://localhost:3000")
        await asyncio.Future()  # 永久运行

asyncio.run(main())
```

### 3.3 客户端实现

#### 原生 JavaScript

```javascript
// ws-client.js
class WebSocketManager {
    constructor(url, options = {}) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
        this.reconnectDelay = options.reconnectDelay || 1000;
        this.handlers = new Map();
        this.shouldReconnect = true;
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('WebSocket 连接已建立');
            this.reconnectAttempts = 0;
            this.emit('open');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.emit('message', data);
                this.emit(data.type, data);  // 触发类型事件
            } catch (e) {
                console.error('解析失败:', e);
                this.emit('rawMessage', event.data);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
            this.emit('error', error);
        };

        this.ws.onclose = (event) => {
            console.log('WebSocket 连接关闭:', event.code, event.reason);
            this.emit('close', event);

            // 自动重连
            if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`${this.reconnectDelay * this.reconnectAttempts}ms 后尝试重连...`);
                setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
            }
        };
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket 未连接');
        }
    }

    on(event, handler) {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, new Set());
        }
        this.handlers.get(event).add(handler);
    }

    emit(event, data) {
        const eventHandlers = this.handlers.get(event);
        if (eventHandlers) {
            eventHandlers.forEach(handler => handler(data));
        }
    }

    close() {
        this.shouldReconnect = false;
        if (this.ws) {
            this.ws.close();
        }
    }
}

// 使用
const ws = new WebSocketManager('ws://localhost:3000', {
    maxReconnectAttempts: 10,
    reconnectDelay: 1000
});

ws.on('open', () => console.log('已连接'));
ws.on('message', (data) => console.log('收到:', data));
ws.on('pong', (data) => console.log('Pong:', data));

ws.connect();

// 发送消息
ws.send({ type: 'chat', message: 'Hello!' });

// 关闭连接
window.addEventListener('beforeunload', () => ws.close());
```

#### React Hook

```javascript
// useWebSocket.js
import { useEffect, useRef, useState, useCallback } from 'react';

function useWebSocket(url, options = {}) {
    const [lastMessage, setLastMessage] = useState(null);
    const [connected, setConnected] = useState(false);
    const wsRef = useRef(null);
    const reconnectAttempts = useRef(0);

    const connect = useCallback(() => {
        const ws = new WebSocket(url);

        ws.onopen = () => {
            setConnected(true);
            reconnectAttempts.current = 0;
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setLastMessage(data);
            } catch (e) {
                setLastMessage({ raw: event.data });
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
        };

        ws.onclose = (event) => {
            setConnected(false);

            // 自动重连
            if (options.reconnect && reconnectAttempts.current < (options.maxReconnectAttempts || 5)) {
                reconnectAttempts.current++;
                setTimeout(connect, options.reconnectDelay || 1000);
            }
        };

        wsRef.current = ws;
    }, [url, options.reconnect, options.maxReconnectAttempts, options.reconnectDelay]);

    useEffect(() => {
        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    const sendMessage = useCallback((data) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        }
    }, []);

    return { lastMessage, connected, sendMessage };
}

// 使用
function ChatRoom({ roomId }) {
    const { lastMessage, connected, sendMessage } = useWebSocket('ws://localhost:3000', {
        reconnect: true,
        maxReconnectAttempts: 10
    });

    const handleSend = () => {
        sendMessage({
            type: 'room-message',
            roomId,
            message: 'Hello!'
        });
    };

    return (
        <div>
            <p>状态: {connected ? '已连接' : '未连接'}</p>
            {lastMessage && <p>收到: {JSON.stringify(lastMessage)}</p>}
            <button onClick={handleSend}>发送</button>
        </div>
    );
}
```

## 四、深度对比

### 4.1 连接特性

| 特性 | SSE | WebSocket |
|------|-----|----------|
| 连接方向 | 单向（服务器推） | 双向 |
| 建立方式 | HTTP 请求 | HTTP 升级 |
| 断开方式 | 自动超时或手动关闭 | 任意一方关闭 |
| 重连 | 自动（EventSource） | 需手动实现 |
| 数据格式 | 仅文本 | 文本或二进制 |
| 最大连接数 | 受 HTTP 连接限制 | 更高（独立协议） |

### 4.2 性能对比

```javascript
// 性能测试脚本
const http = require('http');
const { WebSocketServer } = require('ws');

// 测试 SSE
function testSSE() {
    const iterations = 10000;
    const start = Date.now();

    // SSE 连接，发送 10000 条消息
    // ... 测试代码

    const duration = Date.now() - start;
    console.log(`SSE: ${iterations} 消息耗时 ${duration}ms`);
}

// 测试 WebSocket
function testWebSocket() {
    const iterations = 10000;
    const start = Date.now();

    // WebSocket 连接，发送 10000 条消息
    // ... 测试代码

    const duration = Date.now() - start;
    console.log(`WebSocket: ${iterations} 消息耗时 ${duration}ms`);
}
```

### 4.3 适用场景

```
┌─────────────────────────────────────────────────────────┐
│                     技术选型决策树                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  需要双向通信？                                          │
│      ↓ 是                                               │
│  ┌───────────────────────────────────────┐               │
│  │ WebSocket / Socket.IO                  │               │
│  │ 适用：聊天、游戏，实时协作              │               │
│  └───────────────────────────────────────┘               │
│                                                          │
│      ↓ 否                                                │
│  仅需要服务器推送？                                      │
│      ↓ 是                                               │
│  ┌───────────────────────────────────────┐               │
│  │ SSE 是更好的选择                       │               │
│  │ 适用：通知，监控，进度更新              │               │
│  └───────────────────────────────────────┘               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 五、实战选择

### 5.1 聊天应用

```javascript
// 聊天应用 - WebSocket 是最佳选择

// 原因：
// 1. 需要双向通信（发送消息、接收消息、已读状态）
// 2. 消息频繁交互
// 3. 需要低延迟

// WebSocket 实现
class ChatService {
    constructor() {
        this.rooms = new Map();
    }

    handleMessage(socket, data) {
        switch (data.type) {
            case 'join':
                this.joinRoom(socket, data.roomId);
                break;
            case 'send-message':
                this.sendToRoom(socket, data.roomId, data.message);
                break;
            case 'typing':
                this.broadcastTyping(socket, data.roomId);
                break;
        }
    }
}
```

### 5.2 股票行情

```javascript
// 股票行情 - SSE 足够

// 原因：
// 1. 主要数据流向是服务器→客户端
// 2. 偶尔需要客户端发送订阅/退订请求（可以用普通 HTTP）
// 3. 需要自动重连
// 4. 文本数据为主

// SSE 实现
class StockPriceService {
    constructor() {
        this.clients = new Map();  // symbol -> Set<res>
    }

    subscribe(symbol, res) {
        if (!this.clients.has(symbol)) {
            this.clients.set(symbol, new Set());
        }
        this.clients.get(symbol).add(res);
    }

    broadcast(symbol, price) {
        const clients = this.clients.get(symbol);
        if (clients) {
            const data = `data: ${JSON.stringify({ symbol, price })}\n\n`;
            clients.forEach(res => res.write(data));
        }
    }
}
```

### 5.3 在线协作编辑

```javascript
// 多人协作编辑 - WebSocket

// 原因：
// 1. 需要双向同步光标位置
// 2. 操作指令双向传递
// 3. 低延迟要求高

// 使用 WebSocket + OT/CRDT 算法
class CollabServer {
    constructor() {
        this.documents = new Map();
    }

    handleOperation(socket, data) {
        const doc = this.documents.get(data.docId);
        const operation = this.transform(data.operation, doc.pending);

        doc.apply(operation);
        doc.pending.push(operation);

        // 广播给其他用户
        socket.to(data.docId).emit('operation', {
            userId: socket.id,
            operation
        });
    }
}
```

### 5.4 进度更新

```javascript
// 长任务进度 - SSE 更简单

// 原因：
// 1. 单向数据流
// 2. 不需要频繁交互
// 3. SSE 基于 HTTP，更容易通过代理

// Express + SSE 实现
app.get('/long-task/progress', (req, res) => {
    res.set({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    });

    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        res.write(`data: ${JSON.stringify({ progress })}\n\n`);

        if (progress >= 100) {
            clearInterval(interval);
            res.end();
        }
    }, 1000);

    req.on('close', () => clearInterval(interval));
});
```

## 六、反向代理配置

### 6.1 Nginx 配置

```nginx
# SSE 配置
location /events {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    proxy_cache off;
    proxy_buffering off;
}

# WebSocket 配置
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}
```

### 6.2 Caddy 配置

```caddy
# SSE
:3000/events {
    reverse_proxy localhost:3001
}

# WebSocket
:3000/ws {
    reverse_proxy localhost:3001 {
        header_up Connection "Upgrade"
        header_up Upgrade websocket
    }
}
```

## 七、错误处理与重连

### 7.1 SSE 重连

```javascript
// EventSource 自动重连，但可以监听重连事件
const eventSource = new EventSource('/events');

let reconnectAttempts = 0;

eventSource.onerror = (error) => {
    console.error('SSE 错误:', error);

    if (eventSource.readyState === EventSource.CLOSED) {
        console.log('SSE 连接已关闭，准备重连');
        setTimeout(() => {
            reconnectAttempts++;
            console.log(`重连尝试 ${reconnectAttempts}`);
            eventSource.close();
            // 重新创建 EventSource
        }, 1000 * reconnectAttempts);
    }
};

// 监听自定义的重连事件
eventSource.addEventListener('reconnect', (event) => {
    const data = JSON.parse(event.data);
    console.log('服务端要求重连:', data);
});
```

### 7.2 WebSocket 重连

```javascript
// 指数退避重连
class SmartReconnect {
    constructor() {
        this.maxDelay = 30000;
        this.baseDelay = 1000;
    }

    getDelay(attempts) {
        const delay = Math.min(
            this.baseDelay * Math.pow(2, attempts),
            this.maxDelay
        );
        // 添加随机抖动
        return delay * (0.5 + Math.random() * 0.5);
    }
}

// 心跳保活
class HeartbeatManager {
    constructor(ws, options = {}) {
        this.ws = ws;
        this.interval = options.interval || 30000;
        this.timeout = options.timeout || 5000;
        this.timer = null;
        this.timeoutTimer = null;
    }

    start() {
        this.timer = setInterval(() => {
            this.sendPing();
        }, this.interval);
    }

    sendPing() {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));

            this.timeoutTimer = setTimeout(() => {
                console.warn('心跳超时，关闭连接');
                this.ws.close();
            }, this.timeout);
        }
    }

    onPong() {
        if (this.timeoutTimer) {
            clearTimeout(this.timeoutTimer);
        }
    }

    stop() {
        if (this.timer) clearInterval(this.timer);
        if (this.timeoutTimer) clearTimeout(this.timeoutTimer);
    }
}
```

## 八、安全考虑

### 8.1 认证

```javascript
// SSE 认证 - 通过查询参数或 Cookie
app.get('/events', (req, res) => {
    const token = req.query.token || req.cookies.token;

    if (!validateToken(token)) {
        res.writeHead(401);
        res.end('Unauthorized');
        return;
    }

    // 建立 SSE 连接
});

// WebSocket 认证 - 握手时验证
wss.on('connection', (ws, req) => {
    const token = parseToken(req);

    if (!validateToken(token)) {
        ws.close(4001, 'Unauthorized');
        return;
    }

    ws.userId = token.userId;
});
```

### 8.2 速率限制

```javascript
// 消息速率限制
class RateLimiter {
    constructor(maxMessages, windowMs) {
        this.maxMessages = maxMessages;
        this.windowMs = windowMs;
        this.clients = new Map();
    }

    check(clientId) {
        const now = Date.now();
        const client = this.clients.get(clientId);

        if (!client) {
            this.clients.set(clientId, [now]);
            return true;
        }

        // 清理过期记录
        const recent = client.filter(t => now - t < this.windowMs);

        if (recent.length >= this.maxMessages) {
            return false;
        }

        recent.push(now);
        this.clients.set(clientId, recent);
        return true;
    }
}
```

## 九、总结

### 9.1 选型建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| 聊天应用 | WebSocket | 双向、低延迟、频繁交互 |
| 股票行情 | SSE | 单向、有重连、HTTP 兼容 |
| 游戏 | WebSocket | 极低延迟、二进制数据 |
| 邮件通知 | SSE | 单向、简单、HTTP 兼容 |
| 协作编辑 | WebSocket | 双向同步、低延迟 |
| 进度更新 | SSE | 单向、简单、自动重连 |

### 9.2 核心要点

1. **SSE 基于 HTTP，适合单向服务器推送场景**
2. **WebSocket 独立协议，适合双向实时通信**
3. **SSE 自动重连，WebSocket 需手动实现**
4. **WebSocket 支持二进制，SSE 仅文本**
5. **通过反向代理时，WebSocket 需要特殊配置**

### 9.3 最佳实践

- ✅ 单向推送优先选择 SSE
- ✅ 双向通信选择 WebSocket
- ✅ 实现心跳保活机制
- ✅ 使用重连和退避策略
- ✅ 通过 WSS/HTTPS 加密传输
- ❌ 不要用 SSE 做高频交易
- ❌ 不要用 WebSocket 做简单通知

> 如果对你有帮助，欢迎点赞、收藏！有任何问题欢迎在评论区讨论。
