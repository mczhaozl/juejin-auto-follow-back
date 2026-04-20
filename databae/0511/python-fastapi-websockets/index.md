# Python FastAPI WebSockets 完全指南

## 一、基础 WebSocket

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Received: {data}")
```

## 二、广播

```python
from typing import List

clients: List[WebSocket] = []

@app.websocket("/ws/broadcast")
async def broadcast_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                await client.send_text(data)
    finally:
        clients.remove(websocket)
```

## 三、WebSocket 依赖

```python
async def get_token(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
    return token
```

## 四、前端连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => console.log(event.data);
ws.send('Hello server');
```

## 五、最佳实践

- 限制连接数防止攻击
- 处理断开连接和重连
- 使用 token 认证
- 消息队列解耦
- 使用 WebSocket 库优化
