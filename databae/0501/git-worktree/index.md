# Git Worktree 高级工作流完全指南：多分支并行开发

## 一、Git Worktree 概述

### 1.1 什么是 Worktree

Git Worktree 允许在同一个仓库中同时检出多个分支。

### 1.2 优势

- 无需频繁切换分支
- 同时进行多个功能开发
- 方便测试和对比

---

## 二、基本用法

### 2.1 创建 Worktree

```bash
# 为分支创建 worktree
git worktree add ../feature-branch feature

# 创建新分支并检出
git worktree add -b new-feature ../new-feature

# 从指定 commit 创建
git worktree add ../hotfix abc123
```

### 2.2 查看 Worktree

```bash
# 列出所有 worktree
git worktree list

# 输出示例
/path/to/main-repo      abc123 [main]
/path/to/feature-branch def456 [feature]
/path/to/hotfix         789abc (detached HEAD)
```

### 2.3 进入 Worktree 工作

```bash
cd ../feature-branch

# 正常的 git 操作
git status
git add .
git commit -m "..."
git push
```

---

## 三、典型工作流

### 3.1 并行开发

```bash
# 主仓库
cd main-repo
git checkout main

# 创建功能分支 worktree
git worktree add ../feature-x feature-x
git worktree add ../feature-y feature-y

# 同时开发多个功能
cd ../feature-x
# 开发功能 X...

cd ../feature-y
# 开发功能 Y...
```

### 3.2 Hotfix 工作流

```bash
# 在主仓库开发新功能
cd main-repo
git checkout develop

# 需要处理紧急 bug
git worktree add -b hotfix-123 ../hotfix main

cd ../hotfix
# 修复 bug...
git commit -m "Fix critical bug"
git push origin hotfix-123

# 回到主仓库继续开发
cd ../main-repo
```

### 3.3 PR 审查

```bash
# 查看 PR
git worktree add ../pr-123 pr-123
cd ../pr-123
# 审查代码...

# 查看另一个 PR
git worktree add ../pr-456 pr-456
```

---

## 四、管理 Worktree

### 4.1 删除 Worktree

```bash
# 删除 worktree
git worktree remove ../feature-branch

# 强制删除（有未提交的更改）
git worktree remove --force ../feature-branch

# 删除目录后清理
git worktree prune
```

### 4.2 移动 Worktree

```bash
git worktree move ../old-location ../new-location
```

### 4.3 锁定 Worktree

```bash
git worktree lock ../important-worktree
git worktree unlock ../important-worktree
```

---

## 五、高级技巧

### 5.1 共享配置

```bash
# worktree 共享 .git/config
# 可以单独设置 user.name 等

cd ../feature-x
git config user.name "Feature X Dev"
```

### 5.2 共用依赖

```bash
# 使用符号链接共享 node_modules
cd main-repo
git worktree add ../feature feature
cd ../feature
ln -s ../main-repo/node_modules .
```

### 5.3 与 Bisect 配合

```bash
git worktree add ../bisect-test
cd ../bisect-test
git bisect start
git bisect bad HEAD
git bisect good v1.0
```

---

## 六、实战场景

### 6.1 多版本维护

```bash
# 主仓库 - 开发
git worktree add ../main main

# v1.0 分支 - 维护
git worktree add ../v1.0 v1.0

# v2.0 分支 - 维护
git worktree add ../v2.0 v2.0

# 同时修复多个版本的 bug
cd ../v1.0
# 修复 v1.0 的 bug...

cd ../v2.0
# 修复 v2.0 的 bug...
```

### 6.2 大重构

```bash
# 主仓库 - 正常开发
cd main-repo

# 创建重构 worktree
git worktree add ../refactor refactor
cd ../refactor

# 进行大重构...
# 不影响主仓库的开发进度
```

---

## 七、注意事项

### 7.1 限制

- 同一分支不能有多个 worktree
- 不要删除 worktree 目录，要用 git worktree remove
- worktree 共享同一个 .git 目录

### 7.2 最佳实践

- worktree 目录放在仓库外面
- 使用清晰的命名规范
- 及时清理不用的 worktree

---

## 八、命令速查

```bash
# 创建
git worktree add <path> <branch>
git worktree add -b <new-branch> <path>

# 查看
git worktree list

# 删除
git worktree remove <path>
git worktree prune

# 管理
git worktree move <old> <new>
git worktree lock <path>
git worktree unlock <path>
```

---

## 总结

Git Worktree 是一个强大的工具，可以大幅提升多分支并行开发的效率。通过合理使用，可以避免频繁切换分支带来的麻烦，让工作更加流畅。
