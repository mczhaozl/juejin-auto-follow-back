# SSH 完全指南：远程登录与安全连接

> 深入讲解 SSH 远程登录，包括密钥认证、端口转发、配置优化，以及实际项目中的服务器管理和安全实践。

## 一、SSH 基础

### 1.1 什么是 SSH

安全远程登录协议：

```
┌─────────────┐      SSH 隧道      ┌─────────────┐
│  本地主机   │ ◀──────────────▶ │   远程服务器  │
│  (Client)   │    加密传输       │   (Server)   │
└─────────────┘                    └─────────────┘

端口: 22
协议: SSH v2
```

### 1.2 基本连接

```bash
# 密码登录
ssh user@hostname
ssh -p 22 user@hostname

# 指定密钥
ssh -i ~/.ssh/my_key user@hostname
```

## 二、密钥认证

### 2.1 生成密钥

```bash
# 生成 RSA 密钥
ssh-keygen -t rsa -b 4096 -C "your@email.com"

# 生成 Ed25519（推荐）
ssh-keygen -t ed25519 -C "your@email.com"

# 指定文件名
ssh-keygen -t ed25519 -f ~/.ssh/my_server -C "your@email.com"
```

### 2.2 部署公钥

```bash
# 方法1: ssh-copy-id
ssh-copy-id user@hostname

# 方法2: 手动复制
cat ~/.ssh/id_rsa.pub
# 复制到服务器 ~/.ssh/authorized_keys
```

### 2.3 密钥管理

```bash
# 添加到 ssh-agent
ssh-add ~/.ssh/id_rsa

# 列出密钥
ssh-add -l

# 删除密钥
ssh-add -d ~/.ssh/id_rsa
```

## 三、SSH 配置

### 3.1 用户配置

```bash
# ~/.ssh/config
Host myserver
    HostName 192.168.1.100
    User admin
    Port 22
    IdentityFile ~/.ssh/id_rsa
    
Host github
    HostName github.com
    User git
    IdentityFile ~/.ssh/github

Host *
    AddKeysToAgent yes
    ServerAliveInterval 60
```

### 3.2 服务器配置

```bash
# /etc/ssh/sshd_config
Port 22
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
```

## 四、端口转发

### 4.1 本地端口转发

```bash
# 本地 8080 -> 远程 80
ssh -L 8080:localhost:80 user@remote

# 完整语法
ssh -L [本地端口]:[远程地址]:[远程端口] user@remote
```

### 4.2 远程端口转发

```bash
# 远程 8080 -> 本地 80
ssh -R 8080:localhost:80 user@remote
```

### 4.3 动态端口转发

```bash
# SOCKS 代理
ssh -D 1080 user@remote

# 浏览器配置 SOCKS5 127.0.0.1:1080
```

## 五、SSH 隧道

### 5.1 跳板机连接

```bash
# 跳板机 -> 目标服务器
ssh -J user@bastion user@target

# 多个跳板机
ssh -J user1@jump1,user2@jump2 user@target
```

### 5.2 保持连接

```bash
# 客户端配置
# ~/.ssh/config
ServerAliveInterval 60
ServerAliveCountMax 3

# 服务端配置
# /etc/ssh/sshd_config
ClientAliveInterval 60
ClientAliveCountMax 3
```

## 六、安全实践

### 6.1 禁用密码登录

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
ChallengeResponseAuthentication no
```

### 6.2 防火墙配置

```bash
# ufw
ufw allow 22/tcp
ufw enable

# iptables
iptables -A INPUT -p tcp --dport 22 -j DROP
iptables -A INPUT -p tcp --dport 22 -s 允许的IP -j ACCEPT
```

### 6.3 Fail2Ban

```bash
# 安装
apt install fail2ban

# 配置
# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
```

## 七、实战案例

### 7.1 远程开发

```bash
# SSH 远程开发
ssh -L 3000:localhost:3000 user@dev-server

# VS Code Remote
code --remote ssh-remote+user@hostname /project
```

### 7.2 隧道访问数据库

```bash
# MySQL 隧道
ssh -L 3306:localhost:3306 user@db-server

# Redis 隧道
ssh -L 6379:localhost:6379 user@redis-server
```

## 八、总结

SSH 核心要点：

1. **密钥认证**：更安全
2. **配置**：简化连接
3. **端口转发**：穿透防火墙
4. **跳板机**：安全访问
5. **防火墙**：限制访问
6. **Fail2Ban**：防暴力破解

掌握这些，远程管理 so easy！

---

**推荐阅读**：
- [SSH 官方文档](https://www.ssh.com/academy/ssh)

**如果对你有帮助，欢迎点赞收藏！**
