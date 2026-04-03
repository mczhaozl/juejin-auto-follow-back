# 那个因为 Git 分支管理混乱而加班到凌晨的周五晚上

这是一个关于 Git 分支管理的职场故事，希望能给你一些启发。

## 一、背景

我还记得那个周五的下午，阳光透过窗户洒在办公桌上，一切看起来都很美好。我们团队正在开发一个重要的新功能，计划在下周一上线。

"今天下班前把代码合并到主分支，下周一直接上线！" 项目经理在群里发了消息。

大家都开始忙碌起来，各自的功能分支都准备得差不多了。

## 二、问题出现

我正在处理最后一个 bug，突然收到了测试同学的消息：

"主分支出问题了！页面直接白屏！"

我心里一紧，赶紧切到主分支查看。

```bash
git checkout main
git pull
npm run dev
```

果然，页面一片空白，控制台报错：

```
Uncaught TypeError: Cannot read properties of undefined
```

## 三、排查过程

我开始查看 Git 历史：

```bash
git log --oneline -10
```

发现最近有 5 个合并提交，都是不同同事的功能分支。我开始逐个回滚：

```bash
git revert HEAD~1
```

回滚第一个，问题还在；
回滚第二个，问题还在；
回滚第三个，问题还在；
回滚第四个，问题消失了！

原来是第四个合并引入的 bug。我查看了那个分支的代码，发现：

```javascript
// 原来的代码
const config = getConfig();
const apiUrl = config.api.url;

// 被修改后的代码
const config = getConfig();
const apiUrl = config.api.baseUrl;
```

但是，`config.api` 根本没有 `baseUrl` 这个属性！

## 四、根本原因

事后复盘，我们发现了几个问题：

1. **没有分支策略**：大家直接往主分支合并
2. **没有代码审查**：合并前没人看代码
3. **没有自动化测试**：CI/CD 流程不完善
4. **没有统一的测试环境**：每个人本地环境不一样

## 五、解决方案

痛定思痛，我们引入了 Git Flow 工作流：

### 1. 分支策略

```
main
  └── develop
        ├── feature/user-auth
        ├── feature/payment
        ├── release/v1.0.0
        └── hotfix/login-bug
```

### 2. 保护主分支

在 GitHub/GitLab 设置：
- 主分支不允许直接推送
- 必须通过 Pull Request 合并
- 至少需要 1 人审查
- CI 必须通过

### 3. CI/CD 流程

```yaml
name: CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm test
      - run: npm run build
```

## 六、结果

实施这些改进后：
- 主分支再也没出过类似问题
- 代码质量明显提升
- 团队协作更加顺畅
- 大家下班都更早了！

## 七、总结

Git 分支管理不是小事，它直接影响：
- 代码质量
- 开发效率
- 团队士气
- 你的下班时间

好的分支策略+代码审查+自动化测试=安心的周五晚上！
