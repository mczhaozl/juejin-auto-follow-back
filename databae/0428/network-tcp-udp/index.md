# TCP/IP 与 UDP 协议深度解析：从三次握手到 Socket 编程

## 一、网络模型

### 1.1 OSI 七层模型

| 层级 | 名称 | 协议 |
|-----|------|------|
| 7 | 应用层 | HTTP, FTP, DNS |
| 6 | 表示层 | SSL, JPEG |
| 5 | 会话层 | Sockets |
| 4 | 传输层 | TCP, UDP |
| 3 | 网络层 | IP |
| 2 | 数据链路层 | Ethernet |
| 1 | 物理层 | 网线、光纤 |

### 1.2 TCP/IP 四层模型

| 层级 | 协议 |
|-----|------|
| 应用层 | HTTP, SSH, FTP |
| 传输层 | TCP, UDP |
| 网际层 | IP, ICMP |
| 网络接口层 | Ethernet, PPP |

---

## 二、TCP 详解

### 2.1 TCP 特点

- 面向连接（Connection-oriented）
- 可靠传输（Reliable）
- 字节流（Stream-based）
- 全双工（Full-duplex）
- 拥塞控制（Congestion control）

### 2.2 三次握手

```
    Client              Server
      │                   │
      │── SYN = 1 ──────→│
      │   Seq = x        │
      │                   │
      │←── SYN = 1, ACK = 1 ──│
      │   Seq = y, Ack = x+1  │
      │                   │
      │── ACK = 1 ──────→│
      │   Ack = y+1      │
      │                   │
      │  连接已建立！       │
```

### 2.3 四次挥手

```
    Client              Server
      │                   │
      │── FIN = 1 ──────→│  (1) 客户端关闭
      │   Seq = u        │
      │                   │
      │←── ACK = 1 ──────│  (2) 服务端确认
      │   Ack = u+1      │
      │                   │
      │←── FIN = 1, ACK = 1│  (3) 服务端关闭
      │   Seq = v, Ack = u+1│
      │                   │
      │── ACK = 1 ──────→│  (4) 客户端确认
      │   Ack = v+1      │
```

---

## 三、UDP 详解

### 3.1 UDP 特点

- 无连接（Connectionless）
- 不可靠（Unreliable）
- 数据报（Datagram）
- 开销小、速度快

### 3.2 TCP vs UDP

| 特性 | TCP | UDP |
|-----|-----|-----|
| 连接 | 有 | 无 |
| 可靠性 | 可靠 | 不可靠 |
| 顺序 | 有序 | 不保证 |
| 头部大小 | 20-60 字节 | 8 字节 |
| 适用 | HTTP, FTP, SSH | DNS, 直播, 游戏 |

---

## 四、TCP 头部

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port           |       Destination Port       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Acknowledgment Number                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |Reser- |U|A|P|R|S|F|      |      |
| Offset|ved   |R|C|S|S|Y|I|      |      |
|       |      |G|K|H|T|N|N|Window | Checksum | Urgent Pointer |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options (if any)                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                             Data                              |
```

---

## 五、Socket 编程基础

### 5.1 TCP Server (Node.js)

```javascript
import net from 'net';

const server = net.createServer((socket) => {
  console.log('Client connected');
  
  socket.on('data', (data) => {
    console.log('Received:', data.toString());
    socket.write('Echo: ' + data);
  });
  
  socket.on('end', () => {
    console.log('Client disconnected');
  });
});

server.listen(8080, '127.0.0.1', () => {
  console.log('TCP Server listening on port 8080');
});
```

### 5.2 TCP Client

```javascript
import net from 'net';

const client = net.createConnection({ port: 8080, host: '127.0.0.1' }, () => {
  console.log('Connected to server');
  client.write('Hello from client!');
});

client.on('data', (data) => {
  console.log('Server says:', data.toString());
  client.end();
});

client.on('end', () => {
  console.log('Disconnected');
});
```

### 5.3 UDP Server

```javascript
import dgram from 'dgram';

const server = dgram.createSocket('udp4');

server.on('message', (msg, rinfo) => {
  console.log(`From ${rinfo.address}:${rinfo.port}: ${msg}`);
  server.send(`Echo: ${msg}`, rinfo.port, rinfo.address);
});

server.bind(8080, '127.0.0.1', () => {
  console.log('UDP Server listening');
});
```

---

## 六、TCP 流控制与拥塞控制

### 6.1 流量控制 (Flow Control)

使用滑动窗口，防止发送方淹没接收方。

### 6.2 拥塞控制 (Congestion Control)

- 慢启动 (Slow Start)
- 拥塞避免 (Congestion Avoidance)
- 快速重传 (Fast Retransmit)
- 快速恢复 (Fast Recovery)

---

## 七、HTTP 协议回顾

### 7.1 HTTP/1.1、HTTP/2、HTTP/3

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|-----|---------|-------|-------|
| 协议 | TCP | TCP | QUIC (UDP) |
| 多路复用 | 无 | 有 | 有 |
| 头部压缩 | 无 | HPACK | QPACK |
| 头部阻塞 | 有 | 有 | 无 |

---

## 八、常见端口

| 端口 | 协议 | 用途 |
|-----|------|------|
| 20-21 | FTP | 文件传输 |
| 22 | SSH | 安全终端 |
| 25 | SMTP | 邮件发送 |
| 53 | DNS | 域名解析 |
| 80 | HTTP | 网页服务 |
| 443 | HTTPS | 加密网页 |

---

## 九、抓包与诊断

### 9.1 Wireshark 与 tcpdump

```bash
# tcpdump
tcpdump -i any port 80
tcpdump -i eth0 host 192.168.1.100

# Wireshark 过滤器
tcp.port == 80 && http
```

---

## 十、最佳实践

1. **选择合适的传输层协议**：HTTP → TCP，实时流 → UDP
2. **处理 TCP 粘包问题**：使用分隔符或长度前缀
3. **设置超时与重试**
4. **监听正确的网络接口**

---

## 十一、总结

TCP/IP 是网络的基石，理解其工作原理对开发与调试网络应用至关重要。
