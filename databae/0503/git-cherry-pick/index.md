# Git Cherry-pick 高级技巧完全指南

## 一、Cherry-pick 概述

### 1.1 什么是 Cherry-pick

选择某个分支的特定提交应用到当前分支。

### 1.2 使用场景

- 修复 bug 移植
- 功能回退
- 发布分支管理

---

## 二、基础用法

```bash
# Cherry-pick 单个提交
git cherry-pick <commit-hash>

# 查看提交历史
git log --oneline
```

---

## 三、多个提交

```bash
# 多个连续提交
git cherry-pick A..B

# 包含 A 的范围
git cherry-pick A^..B

# 不连续的提交
git cherry-pick commit1 commit2 commit3
```

---

## 四、冲突处理

```bash
# 遇到冲突时
git cherry-pick abc123
# 冲突！

# 解决冲突
# 编辑文件...
git add <resolved-files>

# 继续
git cherry-pick --continue

# 跳过
git cherry-pick --skip

# 中止
git cherry-pick --abort
```

---

## 五、常用选项

```bash
# 不自动提交
git cherry-pick -n <commit>

# 编辑提交信息
git cherry-pick -e <commit>

# 不提交，但使用原提交消息
git cherry-pick -x <commit>

# 只记录，不改变工作区
git cherry-pick --strategy-option theirs <commit>
```

---

## 六、实战场景

### 6.1 Bug 修复移植

```bash
# 修复 bug
git checkout -b fix main
git commit -m "fix: login bug"

# 移植到生产分支
git checkout production
git cherry-pick <fix-commit>
```

### 6.2 特性分支移植

```bash
git checkout feature
git commit -m "feat: add button"
git commit -m "fix: button color"

# 移植到 main
git checkout main
git cherry-pick <commit1> <commit2>
```

---

## 七、撤销 Cherry-pick

```bash
# 刚 cherry-pick，未 push
git reset --hard HEAD~1

# 已 push
git revert <cherry-picked-commit>
```

---

## 八、高级技巧

```bash
# Cherry-pick 并修改信息
git cherry-pick -e <commit>

# 保持原提交者
git cherry-pick -m 1 <merge-commit>

# 从 reflog 恢复
git cherry-pick HEAD@{5}
```

---

## 九、最佳实践

- 确保测试通过
- 提交尽量小而完整
- 使用 -x 记录原始提交
- 提交信息添加 (cherry-picked) 标注

---

## 总结

Cherry-pick 是强大的 Git 工具，帮助我们灵活管理代码变化，正确使用可以大大提高效率。
