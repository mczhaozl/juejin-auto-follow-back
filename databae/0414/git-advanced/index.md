# Git 高级完全指南：分支策略与协作流程

> 深入讲解 Git 高级特性，包括分支管理、合并策略、标签使用，以及 Git Flow、GitHub Flow 工作流和实际项目中的协作规范。

## 一、分支操作

### 1.1 基本分支

```bash
# 创建分支
git branch feature/login

# 切换分支
git checkout feature/login

# 创建并切换
git checkout -b feature/login

# 删除分支
git branch -d feature/login

# 强制删除
git branch -D feature/login
```

### 1.2 远程分支

```bash
# 推送分支
git push origin feature/login

# 拉取远程分支
git checkout -b feature/login origin/feature/login

# 删除远程分支
git push origin --delete feature/login
```

### 1.3 跟踪分支

```bash
# 设置跟踪
git branch -u origin/feature feature/feature

# 查看跟踪
git branch -vv
```

## 二、合并与变基

### 2.1 merge

```bash
# 合并分支
git checkout main
git merge feature/login

# 禁用快进合并
git merge --no-ff feature/login
```

### 2.2 rebase

```bash
# 变基
git checkout feature/login
git rebase main

# 交互式变基
git rebase -i HEAD~3
```

### 2.3 对比

| 操作 | 特点 |
|------|------|
| merge | 保留完整历史 |
| rebase | 线性历史 |

## 三、工作流

### 3.1 Git Flow

```
main ─────●────────────────●────────────
          ↑                ↑
          └────●──●──●────┘
               feature
```

分支：

- **main**：生产代码
- **develop**：开发代码
- **feature/**：功能分支
- **release/**：发布分支
- **hotfix/**：紧急修复

### 3.2 GitHub Flow

```
main ─●──●──●──●──●──●──●──●──●
       ↑  ↑  ↑  ↑
       feature/1 feature/2
```

流程：

1. 创建分支
2. 提交更改
3. 开启 PR
4. 审核代码
5. 合并上线

## 四、标签

### 4.1 创建标签

```bash
# 轻量标签
git tag v1.0.0

# 附注标签
git tag -a v1.0.0 -m "Release v1.0.0"

# 推送标签
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

### 4.2 删除标签

```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin --delete v1.0.0
```

## 五、实用技巧

### 5.1 暂存

```bash
# 暂存更改
git stash

# 暂存并命名
git stash save "work in progress"

# 查看暂存
git stash list

# 恢复暂存
git stash pop

# 删除暂存
git stash drop
```

### 5.2 交互式暂存

```bash
git add -i
git add -p
```

### 5.3 查找问题

```bash
# 查找 bug
git bisect start
git bisect bad
git bisect good v1.0.0

# 查看谁改的
git blame file.js
```

## 六、总结

Git 高级核心要点：

1. **分支**：创建、切换、删除
2. **merge vs rebase**：合并策略
3. **Git Flow**：经典工作流
4. **GitHub Flow**：轻量工作流
5. **标签**：版本管理

掌握这些，Git 协作更顺畅！

---

**推荐阅读**：
- [Pro Git 书籍](https://git-scm.com/book/zh/v2)

**如果对你有帮助，欢迎点赞收藏！**
