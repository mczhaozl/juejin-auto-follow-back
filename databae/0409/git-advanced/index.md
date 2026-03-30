# Git 高级技巧：分支管理、Rebase 与工作流实战

> 深入讲解 Git 高级操作，包括分支管理、Rebase vs Merge、Git Flow 工作流，以及常见问题的解决技巧。

## 一、分支管理

### 1.1 分支基础

```bash
# 创建分支
git branch feature/login

# 切换分支
git checkout feature/login
git switch feature/login  # Git 2.23+

# 创建并切换
git checkout -b feature/login
git switch -c feature/login

# 查看分支
git branch -a

# 删除分支
git branch -d feature/login
git branch -D feature/login  # 强制删除
```

### 1.2 远程分支

```bash
# 推送分支
git push origin feature/login

# 删除远程分支
git push origin --delete feature/login

# 跟踪远程分支
git checkout --track origin/feature/login
```

## 二、Rebase vs Merge

### 2.1 Merge

```bash
# 合并分支
git checkout main
git merge feature/login

# 产生合并提交
*   Merge branch 'feature/login'
|\
| * commit C
* | commit B
|/
* commit A
```

### 2.2 Rebase

```bash
# 变基到 main
git checkout feature/login
git rebase main

# 结果：线性历史
* commit C' (after rebase)
* commit B
* commit A
```

### 2.3 何时用哪个

| 场景 | 推荐 |
|------|------|
| 公共分支 | Merge |
| 个人功能分支 | Rebase |
| 保持历史整洁 | Rebase |
| 需要完整历史 | Merge |

## 三、交互式 Rebase

### 3.1 修改历史

```bash
# 修改最近 3 个提交
git rebase -i HEAD~3
```

交互界面：
```bash
pick abc1234 添加登录功能
pick def5678 修复bug
pick ghi9012 更新文档

# 修改为:
pick abc1234 添加登录功能
squash def5678 修复bug
reword ghi9012 更新文档
```

### 3.2 命令说明

```bash
pick   # 保留提交
reword # 修改提交信息
edit   # 暂停以修改
squash # 合并到前一个提交
fixup  # 丢弃提交信息
drop   # 删除提交
```

## 四、Git Flow

### 4.1 分支结构

```
main (生产)
  ↑
develop (开发)
  ↑
  ├── feature/* (功能)
  ├── bugfix/* (修复)
  ├── release/* (发布)
  └── hotfix/* (热修复)
```

### 4.2 命令

```bash
# 开始功能
git flow feature start login

# 完成功能
git flow feature finish login

# 开始发布
git flow release start 1.0.0

# 完成发布
git flow release finish 1.0.0
```

### 4.3 简化版

```bash
# 主分支 + 功能分支
git checkout -b feature/login main

# 开发完成后
git checkout main
git merge --no-ff feature/login
git branch -d feature/login
```

## 五、常见问题

### 5.1 撤销修改

```bash
# 撤销工作区修改
git checkout -- file.txt
git restore file.txt  # Git 2.23+

# 撤销暂存
git reset HEAD file.txt
git restore --staged file.txt

# 撤销提交
git revert HEAD          # 撤销最近提交
git revert abc1234       # 撤销指定提交
```

### 5.2 解决冲突

```bash
# 发生冲突后
# 1. 手动解决冲突
# 2. 标记为已解决
git add file.txt

# 3. 完成合并/变基
git commit
git rebase --continue
```

### 5.3 暂存

```bash
# 暂存当前工作
git stash
git stash push -m "work in progress"

# 恢复暂存
git stash pop
git stash apply

# 查看暂存列表
git stash list

# 创建分支
git stash branch new-branch
```

## 六、实战技巧

### 6.1 查找问题提交

```bash
# 二分查找
git bisect start
git bisect bad        # 当前版本有问题
git bisect good v1.0  # 某个正常版本

# Git 自动遍历，找到问题提交
git bisect reset       # 结束
```

### 6.2 清理

```bash
# 删除未跟踪文件
git clean -fd

# 清理所有
git clean -fdx

# 删除远程已删除的分支
git fetch --prune
```

### 6.3 别名

```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
git config --global alias.last 'log -1 HEAD'
```

## 七、总结

Git 高级技巧：

1. **分支管理**：创建、切换、删除
2. **Rebase**：保持线性历史
3. **交互式 Rebase**：修改提交历史
4. **Git Flow**：团队协作流程
5. **撤销与恢复**：安全操作
6. **问题排查**：bisect 定位

掌握这些，Git 使用更得心应手！

---

**推荐阅读**：
- [Git 官方文档](https://git-scm.com/book/zh/v2)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)

**如果对你有帮助，欢迎点赞收藏！**
