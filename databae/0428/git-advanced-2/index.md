# Git 高级技巧进阶版：从 Bisect 到 Worktree

## 一、二分查找：git bisect

快速定位引入 bug 的提交。

### 1.1 基本用法

```bash
# 启动 bisect
git bisect start

# 标记当前版本有 bug
git bisect bad

# 标记一个已知的好版本
git bisect good v1.0.0

# Git 自动切换到中间版本，测试后标记
git bisect good  # 或 git bisect bad
```

### 1.2 自动二分

```bash
# 使用脚本自动测试
git bisect start HEAD v1.0.0
git bisect run ./test.sh
```

### 1.3 查看与重置

```bash
# 查看 bisect 日志
git bisect log

# 退出 bisect
git bisect reset
```

---

## 二、多工作目录：git worktree

在同一仓库的多个分支同时工作。

### 2.1 创建 Worktree

```bash
# 为分支创建新目录
git worktree add ../my-feature feature-branch

# 路径与分支
cd ../my-feature
git branch  # 显示 feature-branch
```

### 2.2 管理 Worktree

```bash
# 列出所有
git worktree list

# 删除
git worktree remove ../my-feature
git worktree prune  # 清理已删除的
```

### 2.3 临时工作区

```bash
# 创建临时分支用于测试
git worktree add -b temp-pr ../temp-pr
```

---

## 三、存储：git stash

保存未提交的更改。

### 3.1 基础

```bash
# 保存
git stash
git stash push -m "WIP: 未完成的功能"

# 查看
git stash list

# 恢复
git stash pop  # 恢复后删除
git stash apply stash@{1}  # 保留记录
```

### 3.2 高级

```bash
# 暂存部分更改
git stash push -p  # 交互式选择

# 包含未跟踪的文件
git stash -u

# 只暂存未跟踪的
git stash push --include-untracked
```

---

## 四、历史与提交修改

### 4.1 修改最近提交

```bash
# 修改提交信息
git commit --amend -m "Better message"

# 添加文件到上一次提交
git add forgotten-file.js
git commit --amend --no-edit
```

### 4.2 修改更早的提交（交互式 rebase）

```bash
git rebase -i HEAD~5
# 在编辑器中修改：
# pick → reword（改信息）
# pick → edit（修改内容）
# pick → squash（合并）
```

---

## 五、高级重置

### 5.1 reset 的三种模式

```bash
# 软重置：保留更改在暂存区
git reset --soft HEAD~3

# 混合重置（默认）：保留更改但取消暂存
git reset --mixed HEAD~3

# 硬重置：丢弃所有更改
git reset --hard HEAD~3
```

### 5.2 安全撤销

```bash
# 使用 reflog 找到旧的提交
git reflog

# 恢复到某一状态
git reset --hard HEAD@{2}
```

---

## 六、Reflog

### 6.1 使用 reflog

```bash
git reflog  # 查看引用变更历史
git reflog --date=iso  # 显示时间

# 恢复误删的分支
git log -g
git branch recover-branch HEAD@{5}
```

---

## 七、樱桃挑选：cherry-pick

### 7.1 单个提交

```bash
# 复制其他分支的提交到当前
git cherry-pick <commit-hash>

# 保留提交者信息
git cherry-pick -x <commit-hash>
```

### 7.2 多个提交

```bash
# 范围（不含起始）
git cherry-pick A..B

# 包含 A
git cherry-pick A^..B

# 不自动提交
git cherry-pick -n
```

---

## 八、补丁与 format-patch

### 8.1 创建与应用

```bash
# 创建最近 3 个提交的补丁
git format-patch -3

# 应用补丁
git apply 0001-my-commit.patch
git am 0001-my-commit.patch  # 保留提交信息
```

---

## 九、Sparse Checkout 与 Monorepo

### 9.1 只检出部分目录

```bash
# 现代 Git (2.25+)
git sparse-checkout init --cone
git sparse-checkout set path/to/needed/directory
```

---

## 十、Bisect 实战

```bash
# 假设 bug 是在 v0.5 到 v1.0 之间引入的

git bisect start HEAD v0.5
git bisect run npm test  # 只要 exit 0 为 good

# 找到第一个 bad 的提交
git bisect good
```

---

## 十一、最佳实践

1. **使用 bisect 快速定位问题**
2. **用 worktree 避免频繁切换分支**
3. **合理使用 stash**
4. **amend 只修改本地提交**
5. **掌握 rebase，小心重写公共历史**

---

## 十二、总结

这些 Git 高级技巧能极大提升工作效率，掌握它们是进阶开发者的必修课。
