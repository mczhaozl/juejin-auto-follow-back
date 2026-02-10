# ⚡ 五倍返回快速开始

> 3分钟配置，让你的粉丝获得5倍关注回报！

## 🎯 你将获得什么？

- ✅ 自动回关所有新粉丝
- ✅ 用5个账号给粉丝5倍回报
- ✅ 完全自动化，无需手动操作
- ✅ 每小时自动执行

## 📋 准备工作

你需要：
- 1个 GitHub 账号（用于运行自动化）
- 1个掘金主账号
- 4个掘金小号（可选，没有也能用）

## 🚀 3步配置

### Step 1: Fork 仓库

点击右上角 **Fork** 按钮，将仓库复制到你的账号

### Step 2: 获取 Cookies

**主账号 Cookie**（必需）：

1. 登录你的掘金主账号
2. 按 `F12` 打开开发者工具
3. 刷新页面
4. 在 Network 标签找到任意 `api.juejin.cn` 请求
5. 复制 Cookie 值（完整的一长串）

**小号 Cookies**（可选）：

重复上述步骤，为每个小号获取 Cookie

### Step 3: 配置 Secrets

在你 Fork 的仓库中：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 Secrets：

#### 必需配置：
- Name: `JUEJIN_COOKIES`
- Value: 粘贴主账号的 Cookie

#### 可选配置（五倍返回）：
- Name: `JUEJIN_COOKIES_ACCOUNT2`，Value: 小号1的 Cookie
- Name: `JUEJIN_COOKIES_ACCOUNT3`，Value: 小号2的 Cookie
- Name: `JUEJIN_COOKIES_ACCOUNT4`，Value: 小号3的 Cookie
- Name: `JUEJIN_COOKIES_ACCOUNT5`，Value: 小号4的 Cookie

**提示**：可以只配置部分小号，比如只配置2个小号就是3倍返回

## ✅ 启用自动化

1. 进入 **Actions** 标签
2. 点击 **"I understand my workflows, go ahead and enable them"**
3. 选择 **"自动回关掘金粉丝"** 工作流
4. 点击 **"Run workflow"** 手动触发测试

## 🎉 完成！

现在：
- ✅ 每小时自动检查新粉丝
- ✅ 自动用所有账号回关
- ✅ 粉丝获得多倍关注回报

## 📊 查看效果

在 Actions 页面查看执行日志：

```
🎯 五倍返回模式启动！共 5 个账号
📋 发现 3 位新粉丝待回关

[主账号] 成功回关 3 人
[小号1] 成功回关 3 人
[小号2] 成功回关 3 人
[小号3] 成功回关 3 人
[小号4] 成功回关 3 人

🎉 五倍返回任务完成！
总计：15 次成功关注
```

## 🔧 常见问题

### Q: 我没有小号怎么办？

只配置主账号也可以，就是普通的自动回关功能。

### Q: Cookie 在哪里找？

按 F12 → Network 标签 → 刷新页面 → 找到 api.juejin.cn 请求 → 复制 Cookie

### Q: Cookie 格式是什么样的？

```
csrf_session_id=xxx; __tea_cookie_tokens_2608=xxx; passport_csrf_token=xxx; ...
```

直接复制粘贴，不需要修改格式！

### Q: 会不会被封号？

正常使用不会，脚本已经做了延时处理（每次操作间隔2秒）。

### Q: Cookie 会过期吗？

会的，大约30天。过期后重新获取并更新 GitHub Secrets 即可。

## 📚 更多文档

- [详细使用指南](./USAGE.md)
- [多账号配置指南](./config/multi-account-setup.md)
- [完整 README](./README.md)

## 🎁 开始享受五倍返回吧！

配置完成后，坐等粉丝增长，你的粉丝会感谢你的慷慨！😄
