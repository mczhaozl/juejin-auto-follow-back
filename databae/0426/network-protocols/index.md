# 网络协议完全指南：从 TCP/IP 到 HTTP/3

网络协议是互联网的基础。本文将带你从基础到高级，全面掌握网络协议。

## 一、TCP/IP 协议栈

### 1. OSI 七层模型

```
应用层 (Layer 7): HTTP, FTP, SMTP, DNS
表示层 (Layer 6): SSL/TLS, 数据加密
会话层 (Layer 5): 会话管理
传输层 (Layer 4): TCP, UDP
网络层 (Layer 3): IP, ICMP
数据链路层 (Layer 2): Ethernet, WiFi
物理层 (Layer 1): 网线, 光纤, 无线电波
```

### 2. TCP/IP 四层模型

```
应用层: HTTP, FTP, SMTP, DNS
传输层: TCP, UDP
网际层: IP, ICMP, ARP
网络接口层: Ethernet, WiFi
```

## 二、IP 协议

### 1. IPv4

```
IPv4 地址格式: 192.168.1.1
- 32 位地址
- 4 个 8 位组
- 约 43 亿个地址

子网掩码: 255.255.255.0
- 网络部分: 192.168.1
- 主机部分: 1

CIDR: 192.168.1.0/24
- /24: 前 24 位是网络位

特殊地址:
- 127.0.0.1: 本地回环
- 10.0.0.0/8: 私有地址
- 172.16.0.0/12: 私有地址
- 192.168.0.0/16: 私有地址
- 0.0.0.0: 所有网络接口
```

### 2. IPv6

```
IPv6 地址格式: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
- 128 位地址
- 8 个 16 位组
- 约 3.4e38 个地址

简写: 2001:db8:85a3::8a2e:370:7334
- 连续的 0 可以省略

特殊地址:
- ::1: 本地回环
- ::/0: 默认路由
- fe80::/10: 链路本地地址
- fc00::/7: 唯一本地地址
```

### 3. ICMP

```
ICMP (Internet Control Message Protocol): 网络控制消息协议

Ping:
- 发送 ICMP Echo Request
- 接收 ICMP Echo Reply

Traceroute:
- 发送 TTL 递增的数据包
- 每跳返回 ICMP Time Exceeded
```

```python
# Python ping 示例
import os
import platform

def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    return os.system(' '.join(command)) == 0

ping('google.com')
```

## 三、TCP 和 UDP

### 1. TCP

```
TCP (Transmission Control Protocol): 传输控制协议
- 面向连接
- 可靠传输
- 有序
- 重传机制
- 流量控制
- 拥塞控制

TCP 三次握手:
1. SYN: 客户端 → 服务器 (SYN=1, seq=x)
2. SYN-ACK: 服务器 → 客户端 (SYN=1, ACK=1, seq=y, ack=x+1)
3. ACK: 客户端 → 服务器 (ACK=1, seq=x+1, ack=y+1)

TCP 四次挥手:
1. FIN: 客户端 → 服务器 (FIN=1, seq=x)
2. ACK: 服务器 → 客户端 (ACK=1, ack=x+1)
3. FIN: 服务器 → 客户端 (FIN=1, seq=y)
4. ACK: 客户端 → 服务器 (ACK=1, ack=y+1)

TCP 端口:
- 0-1023: 知名端口
- 1024-49151: 注册端口
- 49152-65535: 动态端口

常用 TCP 端口:
- 80: HTTP
- 443: HTTPS
- 22: SSH
- 21: FTP
- 25: SMTP
```

### 2. UDP

```
UDP (User Datagram Protocol): 用户数据报协议
- 无连接
- 不可靠
- 无序
- 低开销
- 高速

常用 UDP 端口:
- 53: DNS
- 67/68: DHCP
- 123: NTP
- 5060: SIP
- 161: SNMP
```

### 3. TCP vs UDP

| 特性 | TCP | UDP |
|-----|-----|-----|
| 连接 | 面向连接 | 无连接 |
| 可靠性 | 可靠 | 不可靠 |
| 顺序 | 有序 | 无序 |
| 开销 | 高 | 低 |
| 速度 | 较慢 | 快 |
| 适用场景 | HTTP, FTP, SMTP | DNS, 视频流, 游戏 |

### 4. Socket 编程

```python
# TCP 服务器
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8000))
server.listen(5)

print('Server listening on port 8000')

while True:
    client, addr = server.accept()
    print(f'Connected from {addr}')
    
    data = client.recv(1024)
    print(f'Received: {data.decode()}')
    
    client.send(b'Hello from server')
    client.close()

# TCP 客户端
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8000))

client.send(b'Hello from client')
data = client.recv(1024)
print(f'Received: {data.decode()}')

client.close()

# UDP 服务器
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', 8000))

print('UDP server listening on port 8000')

while True:
    data, addr = server.recvfrom(1024)
    print(f'Received from {addr}: {data.decode()}')
    server.sendto(b'Hello from UDP server', addr)

# UDP 客户端
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b'Hello from UDP client', ('127.0.0.1', 8000))

data, addr = client.recvfrom(1024)
print(f'Received: {data.decode()}')
```

## 四、HTTP 协议

### 1. HTTP/1.1

```
HTTP 请求:
GET /index.html HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: text/html

HTTP 响应:
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 123

<html>...</html>

HTTP 方法:
- GET: 获取资源
- POST: 提交数据
- PUT: 更新资源
- DELETE: 删除资源
- PATCH: 部分更新
- HEAD: 获取头信息
- OPTIONS: 获取支持的方法
- TRACE: 回显请求
- CONNECT: 建立隧道

HTTP 状态码:
- 1xx: 信息
  - 100 Continue
  - 101 Switching Protocols
- 2xx: 成功
  - 200 OK
  - 201 Created
  - 204 No Content
- 3xx: 重定向
  - 301 Moved Permanently
  - 302 Found
  - 304 Not Modified
- 4xx: 客户端错误
  - 400 Bad Request
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 405 Method Not Allowed
- 5xx: 服务器错误
  - 500 Internal Server Error
  - 502 Bad Gateway
  - 503 Service Unavailable
  - 504 Gateway Timeout
```

### 2. HTTP/2

```
HTTP/2 特性:
- 二进制分帧
- 多路复用
- 头部压缩 (HPACK)
- 服务器推送
- 流优先级
```

### 3. HTTP/3

```
HTTP/3 特性:
- 基于 QUIC
- 0-RTT 握手
- 连接迁移
- 更好的拥塞控制
- 内置加密
```

### 4. HTTPS

```
HTTPS = HTTP + TLS

TLS 握手:
1. Client Hello: 支持的密码套件, 随机数
2. Server Hello: 选择密码套件, 证书, 随机数
3. Client Key Exchange: 预主密钥
4. Change Cipher Spec: 切换到加密
5. Finished: 握手完成

证书链:
- 根证书
- 中间证书
- 服务器证书
```

## 五、DNS

### 1. DNS 基础

```
DNS (Domain Name System): 域名系统

域名结构:
www.example.com.
- .: 根域
- com: 顶级域 (TLD)
- example: 二级域
- www: 三级域

DNS 记录类型:
- A: IPv4 地址
- AAAA: IPv6 地址
- CNAME: 别名
- MX: 邮件交换
- NS: 名称服务器
- SOA: 起始授权
- TXT: 文本
- SRV: 服务定位
- PTR: 反向查询

DNS 查询过程:
1. 检查本地缓存
2. 查询递归 DNS 服务器
3. 查询根 DNS 服务器
4. 查询 TLD DNS 服务器
5. 查询权威 DNS 服务器
6. 返回结果
```

### 2. DNS 工具

```bash
# nslookup
nslookup example.com

# dig
dig example.com
dig example.com A
dig example.com MX
dig +trace example.com

# host
host example.com

# Windows
ipconfig /displaydns
ipconfig /flushdns

# Linux/macOS
cat /etc/resolv.conf
sudo systemd-resolve --flush-caches
```

## 六、WebSocket

```
WebSocket: 全双工通信

WebSocket 握手:
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

```javascript
// 浏览器 WebSocket
const ws = new WebSocket('ws://example.com/ws');

ws.onopen = () => {
  console.log('Connected');
  ws.send('Hello from client');
};

ws.onmessage = (event) => {
  console.log('Received:', event.data);
};

ws.onclose = () => {
  console.log('Disconnected');
};

// Node.js WebSocket 服务器
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  ws.on('message', (message) => {
    console.log('Received:', message);
    ws.send('Hello from server');
  });
  
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});
```

## 七、其他协议

### 1. FTP

```
FTP (File Transfer Protocol): 文件传输协议
- 20: 数据端口
- 21: 控制端口

FTPS: FTP + SSL/TLS
SFTP: SSH File Transfer Protocol
```

### 2. SMTP, POP3, IMAP

```
SMTP (Simple Mail Transfer Protocol): 发送邮件
- 端口: 25, 465 (SMTPS), 587 (STARTTLS)

POP3 (Post Office Protocol v3): 接收邮件
- 端口: 110, 995 (POP3S)
- 下载并删除

IMAP (Internet Message Access Protocol): 接收邮件
- 端口: 143, 993 (IMAPS)
- 服务器上管理
```

### 3. SSH

```
SSH (Secure Shell): 安全外壳协议
- 端口: 22

SSH 密钥:
ssh-keygen -t rsa -b 4096
ssh-copy-id user@host

SSH 配置 (~/.ssh/config):
Host myserver
  HostName example.com
  User myuser
  Port 22
  IdentityFile ~/.ssh/myserver
```

## 八、网络工具

### 1. tcpdump

```bash
# 捕获所有流量
tcpdump -i eth0

# 捕获特定端口
tcpdump -i eth0 port 80

# 捕获特定主机
tcpdump -i eth0 host 192.168.1.1

# 写入文件
tcpdump -i eth0 -w capture.pcap

# 读取文件
tcpdump -r capture.pcap
```

### 2. Wireshark

```
Wireshark: 图形化网络协议分析器

过滤器语法:
- ip.addr == 192.168.1.1
- tcp.port == 80
- http
- dns
- ssl
```

### 3. netstat/ss

```bash
# Linux
ss -tuln  # 显示监听端口
ss -tulnp # 显示进程
netstat -tuln

# Windows
netstat -ano
netstat -ano | findstr :80
```

### 4. curl

```bash
# 基本请求
curl https://example.com

# 显示响应头
curl -I https://example.com

# POST 请求
curl -X POST -d "name=John" https://example.com

# 上传文件
curl -F "file=@image.jpg" https://example.com/upload

# 使用代理
curl -x http://proxy:8080 https://example.com

# 保存响应
curl -o output.html https://example.com
```

## 九、最佳实践

1. 使用 HTTPS
2. 启用 HTTP/2 或 HTTP/3
3. 配置 DNS 缓存
4. 使用 CDN
5. 优化 TCP 参数
6. 使用负载均衡
7. 监控网络流量
8. 定期更新证书
9. 使用强密码和密钥
10. 网络分段

## 十、总结

网络协议核心要点：
- TCP/IP 协议栈
- IP (IPv4, IPv6)
- TCP 和 UDP
- HTTP (1.1, 2, 3) 和 HTTPS
- DNS
- WebSocket
- 其他协议 (FTP, SMTP, SSH)
- 网络工具
- 最佳实践

开始深入理解网络协议吧！
