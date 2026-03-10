# OpenClaw 完整本地部署与飞书集成指南

> 从零搭建 OpenClaw AI 助手，接入飞书机器人，10 分钟让团队用上私有化 AI 工作流。

---

## 一、OpenClaw 是什么

OpenClaw 是一个开源的 AI 工作流编排平台，可以把大模型能力封装成可复用的工具和流程，支持多模型切换、工具调用、知识库检索等功能。相比直接调 API，它提供了：

- 可视化流程编排
- 多模型统一接口（OpenAI、Claude、国产模型等）
- 工具扩展机制（搜索、代码执行、数据库查询等）
- 对话历史管理
- 权限与审计

适合团队内部搭建 AI 助手、客服机器人、知识问答等场景。

官方仓库：https://github.com/openclaw/openclaw

## 二、环境准备

### 2.1 系统要求

- 操作系统：Linux / macOS / Windows（推荐 Linux）
- Node.js：18.x 或更高
- 数据库：PostgreSQL 14+ 或 MySQL 8+
- Redis：6.x+（可选，用于缓存和队列）
- 内存：至少 2GB

### 2.2 安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nodejs npm postgresql redis-server

# macOS
brew install node postgresql redis

# 启动服务
sudo systemctl start postgresql redis-server
# macOS 用 brew services start postgresql redis
```

## 三、部署 OpenClaw

### 3.1 克隆代码

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

### 3.2 安装依赖

```bash
npm install
# 或使用 pnpm（更快）
npm install -g pnpm
pnpm install
```

### 3.3 配置数据库

创建数据库：

```bash
# 进入 PostgreSQL
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE openclaw;
CREATE USER openclaw_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE openclaw TO openclaw_user;
\q
```

复制配置文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
# 数据库配置
DATABASE_URL=postgresql://openclaw_user:your_password@localhost:5432/openclaw

# Redis 配置（可选）
REDIS_URL=redis://localhost:6379

# 模型配置
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1

# 或使用国产模型
# ZHIPU_API_KEY=xxx
# QWEN_API_KEY=xxx

# 服务端口
PORT=3000
```

### 3.4 初始化数据库

```bash
npm run db:migrate
npm run db:seed  # 可选，导入示例数据
```

### 3.5 启动服务

```bash
# 开发模式
npm run dev

# 生产模式
npm run build
npm run start
```

访问 `http://localhost:3000`，看到登录页面说明部署成功。

默认账号：`admin@openclaw.com` / `admin123`

## 四、接入飞书机器人

### 4.1 创建飞书应用

1. 进入飞书开放平台：https://open.feishu.cn/
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`
4. 开通「机器人」能力
5. 配置事件订阅地址：`http://your-domain.com/api/feishu/webhook`
6. 订阅事件：`im.message.receive_v1`（接收消息）

### 4.2 配置 OpenClaw

在 `.env` 中添加：

```bash
# 飞书配置
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_VERIFICATION_TOKEN=xxx  # 事件订阅的 Verification Token
FEISHU_ENCRYPT_KEY=xxx         # 可选，加密 Key
```

### 4.3 创建飞书集成

在 OpenClaw 管理后台：

1. 进入「集成管理」
2. 新建集成，选择「飞书机器人」
3. 填入 App ID 和 Secret
4. 配置触发词（如 `@AI助手`）
5. 选择关联的工作流

### 4.4 测试对话

在飞书群聊中：

```
@AI助手 你好
```

机器人应该会回复。如果没反应，检查：

- 事件订阅地址是否可访问（需公网 IP 或内网穿透）
- 日志中是否有报错：`npm run logs`
- 机器人是否已加入群聊

## 五、内网穿透（开发环境）

如果本地开发，飞书无法访问 localhost，需要内网穿透：

### 5.1 使用 ngrok

```bash
# 安装
brew install ngrok  # macOS
# 或从 https://ngrok.com/ 下载

# 启动
ngrok http 3000
```

复制生成的公网地址（如 `https://abc123.ngrok.io`），填入飞书事件订阅地址。

### 5.2 使用 frp（推荐生产）

如果有公网服务器，用 frp 更稳定：

服务端（公网服务器）：

```bash
# 下载 frp
wget https://github.com/fatedier/frp/releases/download/v0.52.0/frp_0.52.0_linux_amd64.tar.gz
tar -xzf frp_0.52.0_linux_amd64.tar.gz
cd frp_0.52.0_linux_amd64

# 编辑 frps.ini
[common]
bind_port = 7000

# 启动
./frps -c frps.ini
```

客户端（本地）：

```bash
# 编辑 frpc.ini
[common]
server_addr = your-server-ip
server_port = 7000

[openclaw]
type = http
local_port = 3000
custom_domains = openclaw.yourdomain.com

# 启动
./frpc -c frpc.ini
```

配置域名解析 `openclaw.yourdomain.com` 到公网服务器 IP。

## 六、生产部署建议

### 6.1 使用 PM2 管理进程

```bash
npm install -g pm2

# 启动
pm2 start npm --name openclaw -- run start

# 开机自启
pm2 startup
pm2 save
```

### 6.2 配置 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name openclaw.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 6.3 配置 HTTPS

```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d openclaw.yourdomain.com
```

### 6.4 数据库备份

```bash
# 定时备份脚本
#!/bin/bash
pg_dump -U openclaw_user openclaw > /backup/openclaw_$(date +%Y%m%d).sql

# 添加到 crontab
0 2 * * * /path/to/backup.sh
```

## 七、常见问题

### 7.1 飞书机器人不回复

- 检查事件订阅地址是否返回 200
- 查看日志：`pm2 logs openclaw`
- 确认 Verification Token 正确
- 机器人需要在群聊中被 @ 才会触发

### 7.2 模型调用失败

- 检查 API Key 是否有效
- 确认 BASE_URL 正确（国内可能需要代理）
- 查看余额是否充足

### 7.3 数据库连接失败

- 检查 PostgreSQL 是否启动：`sudo systemctl status postgresql`
- 确认连接字符串格式正确
- 防火墙是否开放 5432 端口

## 八、进阶配置

### 8.1 多模型切换

在工作流中配置多个模型，根据任务类型自动选择：

```javascript
// 配置文件
models: [
  { name: 'gpt-4', provider: 'openai', tasks: ['complex'] },
  { name: 'gpt-3.5-turbo', provider: 'openai', tasks: ['simple'] },
  { name: 'glm-4', provider: 'zhipu', tasks: ['chinese'] }
]
```

### 8.2 知识库集成

上传文档，让 AI 基于私有知识回答：

1. 进入「知识库管理」
2. 上传 PDF/Word/Markdown 文件
3. 等待向量化完成
4. 在工作流中启用「知识库检索」节点

### 8.3 自定义工具

编写 JavaScript 函数扩展能力：

```javascript
// tools/weather.js
export default {
  name: 'get_weather',
  description: '获取城市天气',
  parameters: {
    city: { type: 'string', required: true }
  },
  async execute({ city }) {
    const res = await fetch(`https://api.weather.com?city=${city}`);
    return res.json();
  }
};
```

## 总结

OpenClaw 部署流程：安装依赖 → 配置数据库 → 启动服务 → 接入飞书。核心步骤：

- 准备 Node.js + PostgreSQL + Redis 环境
- 配置 `.env` 文件（数据库、模型 API Key）
- 初始化数据库并启动服务
- 创建飞书应用，配置事件订阅
- 使用内网穿透或公网服务器暴露接口

生产环境建议用 PM2 + Nginx + HTTPS，定期备份数据库。
