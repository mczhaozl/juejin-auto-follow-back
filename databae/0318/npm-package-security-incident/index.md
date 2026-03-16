# 记一次 npm package 被投毒的经历

> 一次惊心动魄的供应链攻击经历，以及如何保护你的项目。

## 一、那个平静的周二下午

记得那是去年一个普通的周二下午，团队正在有序地推进项目迭代。我负责的前端模块刚好完成了一个功能的开发，正准备提交代码进行 Code Review。

就在这时，运维同事突然在群里发了一条消息：「生产环境出现大量异常请求，你们谁改了什么？」

我心里咯噔一下，打开监控面板一看，好家伙，服务器 CPU 飙升到 100%，错误日志像瀑布一样往下刷。初步判断是某个接口被恶意调用了，但我们的接口都有鉴权和限流，不应该出现这种情况。

更诡异的是，错误日志里出现了大量来自我们自己的域名发起的请求。这说明攻击者可能已经拿到了我们服务器的某种访问凭证。

## 二、排查陷入僵局

我们立即启动了应急响应流程。首先检查了最近部署的代码，没有发现可疑的改动。然后查看了服务器日志，发现所有异常请求都来自一个特定的 User-Agent。

运维同事开始怀疑是服务器被入侵了，但安全团队排查后确认服务器本身没有问题。数据库也没有异常连接，Redis 缓存也正常。

就在大家一筹莫展的时候，我突然注意到一个细节：这些异常请求的时间点，恰好对应了我们早上的一次 npm install。

「会不会是依赖包的问题？」我提出了这个猜测。

## 三、真相浮出水面

我们立即锁定了当天新增的依赖，一个用于处理图片的第三方库。安全同事对这个包进行了深入分析，发现了令人后怕的事实：这个包在安装时会执行 postinstall 脚本，脚本中包含了一段恶意代码。

恶意代码的逻辑大致如下：

1. **窃取环境变量**：读取 `.env` 文件和进程环境变量，收集 API Key、数据库密码等信息
2. **建立后门**：在服务器上创建一个隐蔽的 Webshell，用于后续远程控制
3. **数据外传**：将窃取的信息通过加密通道发送到攻击者的服务器
4. **扩散传播**：尝试感染同一网络下的其他服务器

更可怕的是，这个恶意包还使用了多种反检测技术：
- 恶意代码经过多层混淆和加密
- 只在特定时间段执行，避开工作时间
- 对不同的环境执行不同的行为，降低被发现的风险

## 四、攻击原理分析

事后我们对这次攻击进行了详细的技术分析。npm 生态的供应链攻击主要有以下几种形式：

**1. 恶意代码注入**

攻击者通过各种手段获取了合法 npm 包的发布权限，然后在包中注入恶意代码。由于用户信任这些包，安装时不会过多检查，导致恶意代码在用户机器上执行。

**2. 域名仿冒**

攻击者注册与知名包相似的域名（如 `express-js` 冒充 `express`），诱导用户安装恶意包。这种攻击利用了用户的手误或对包名的不熟悉。

**3. 依赖链攻击**

攻击者不直接攻击知名包，而是攻击这些包依赖的底层依赖。由于很多包依赖大量第三方库，攻击面很大。

**4. Typosquatting**

利用拼写相似的包名（如 `lodash` vs `lodash-js`）进行攻击，用户在搜索或安装时容易误装。

## 五、我们做了什么应急处理

发现问题的第一时间，我们采取了以下措施：

**1. 立即隔离受影响的服务**

```bash
# 停止所有受影响的服务
pm2 stop all

# 删除可疑的依赖包
rm -rf node_modules
rm package-lock.json

# 从 lockfile 中移除可疑包
npm uninstall suspicious-package
```

**2. 轮换所有敏感凭证**

```bash
# 轮换 API Keys
# 轮换数据库密码
# 轮换服务器 SSH 密钥
# 撤销并重新生成所有访问令牌
```

**3. 清理恶意代码**

```bash
# 检查所有服务器是否有可疑文件
find / -name "*.sh" -mtime -1 -type f

# 检查计划任务
crontab -l
cat /etc/crontab

# 检查 SSH authorized_keys
cat ~/.ssh/authorized_keys
```

**4. 通知用户和合作伙伴**

如果你的服务影响到用户，及时通知他们可能的安全风险，并建议他们采取相应的防护措施。

## 六、如何防范供应链攻击

### 6.1 依赖管理最佳实践

**使用 lockfile**

始终使用 lockfile（package-lock.json 或 yarn.lock），确保每次安装的依赖版本完全一致。这可以防止「依赖漂移」攻击。

```json
// package.json
{
  "lockfileVersion": 2,
  "dependencies": {
    "express": {
      "version": "4.18.2",
      "resolved": "https://registry.npmmirror.com/express/-/express-4.18.2.tgz",
      "integrity": "sha512-5/PsL6iGPdfQ/lKM1UuielYgv3BUoJfz1aUwU9vHZ+J7gyvwdQXFEBIEIaxeGf0GIcreATNyBExtalisDbuMqQ=="
    }
  }
}
```

**定期审计依赖**

使用 npm audit 或第三方工具定期检查依赖的安全性：

```bash
# npm 内置审计
npm audit

# 使用 yarn
yarn audit

# 使用更详细的商业工具
npm install -g snyk
snyk test
```

**锁定依赖版本**

尽量使用精确版本号，避免使用 `^` 或 `~` 这样的范围限定符：

```json
// 不推荐
{
  "dependencies": {
    "lodash": "^4.17.21"
  }
}

// 推荐
{
  "dependencies": {
    "lodash": "4.17.21"
  }
}
```

### 6.2 安装时检查

**使用 npm ci 代替 npm install**

`npm ci` 会严格按照 lockfile 安装，不会修改 lockfile，安全性更高：

```bash
npm ci
# 或
npm install --ci-only
```

**检查包的权限和下载量**

在安装陌生包之前，检查其下载量和维护者信息：

```bash
# 查看包的信息
npm view express

# 查看包的下载趋势
npm trends express

# 查看包的所有者
npm owner ls express
```

**使用 --ignore-scripts 限制脚本执行**

对于不信任的包，可以禁止其执行安装脚本：

```bash
npm install suspicious-package --ignore-scripts
```

### 6.3 持续监控

**使用依赖监控服务**

- **Snyk**：提供依赖漏洞扫描和监控
- **Dependabot**：GitHub 的自动依赖更新工具
- **Renovate**：另一个流行的依赖更新工具
- **npm audit**：npm 内置的漏洞扫描

**配置 GitHub Dependabot**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
```

### 6.4 代码审查

**审查依赖变更**

在 Code Review 时，特别关注依赖的变更：

```diff
  "dependencies": {
-   "some-package": "1.0.0",
+   "some-package": "1.1.0",
+   "new-suspicious-package": "2.0.0"
  }
```

**检查 postinstall 脚本**

在安装新包之前，检查其 package.json 中的脚本：

```bash
# 查看包的 package.json
npm view some-package scripts
```

### 6.5 基础设施防护

**使用私有 npm 镜像**

搭建私有 npm 镜像，对所有包进行安全扫描后再允许使用：

```bash
# Verdaccio - 轻量级私有 npm 代理
npm install -g verdaccio
verdaccio
```

**容器化部署**

使用 Docker 等容器技术，确保环境一致性：

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# 先复制 lockfile，确保依赖版本一致
COPY package-lock.json ./
COPY package.json ./

# 安装依赖
RUN npm ci --only=production

# 复制应用代码
COPY . .

# 不以 root 用户运行
USER node
```

## 七、事件复��与改进

这次事件之后，我们团队进行了全面的复盘，并建立了以下机制：

**1. 依赖白名单制度**

只有经过安全评估的包才能添加到项目中，新依赖需要经过审批流程。

**2. 自动化安全扫描**

在 CI/CD 流程中集成安全扫描，每次部署前自动检查依赖漏洞。

**3. 定期依赖更新**

建立定期更新依赖的机制，避免使用过旧版本，减少被已知漏洞影响的风险。

**4. 最小权限原则**

服务器和 API 使用最小权限，避免单点突破导致全面沦陷。

**5. 应急响应预案**

制定详细的应急响应流程，定期演练，确保出现问题时能够快速响应。

## 八、行业内的类似案例

供应链攻击在软件行业并不罕见，以下是几个著名的案例：

**1. event-stream 事件（2018）**

攻击者通过社会工程获取了热门 npm 包 `event-stream` 的发布权限，在包中注入了窃取比特币钱包的恶意代码，影响了数百万用户。

**2. ua-parser-js 事件（2021）**

攻击者向 `ua-parser-js` 包注入了恶意代码，窃取用户凭证和加密货币。该包每天有超过 2000 万次下载，影响范围极广。

**3. colors.js 和 faker.js 事件（2022）**

开源作者 Marak Squires 故意在这两个热门包中引入无限循环代码，导致大量使用这些包的应用崩溃，引发了关于开源可持续性的广泛讨论。

## 九、总结

这次 npm 包供应链攻击事件给我们敲响了警钟。在享受 npm 生态便利的同时，我们也要时刻警惕潜在的安全风险。通过建立完善的依赖管理机制、定期安全审计、自动化监控流程，我们可以大大降低供应链攻击的风险。

安全不是一次性的工作，而是需要持续投入的长期工程。希望这篇文章能帮助你和你的团队避免类似的经历。

如果这篇文章对你有帮助，欢迎点赞、收藏和关注。