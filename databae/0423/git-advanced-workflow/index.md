# Git 高级工作流完全指南：从团队协作到最佳实践

Git 是现代软件开发不可或缺的工具。本文将带你掌握 Git 的高级工作流和最佳实践。

## 一、Git 分支策略

### 1. Git Flow

```bash
# 主分支
main        # 生产环境代码
develop     # 开发分支

# 辅助分支
feature/*   # 功能分支
release/*   # 发布分支
hotfix/*    # 热修复分支

# 创建功能分支
git checkout -b feature/new-feature develop

# 完成功能开发
git checkout develop
git merge --no-ff feature/new-feature
git branch -d feature/new-feature

# 创建发布分支
git checkout -b release/1.0.0 develop

# 发布到生产
git checkout main
git merge --no-ff release/1.0.0
git tag -a 1.0.0

# 合并回 develop
git checkout develop
git merge --no-ff release/1.0.0
git branch -d release/1.0.0

# 热修复
git checkout -b hotfix/1.0.1 main
# 修复...
git checkout main
git merge --no-ff hotfix/1.0.1
git tag -a 1.0.1
git checkout develop
git merge --no-ff hotfix/1.0.1
git branch -d hotfix/1.0.1
```

### 2. GitHub Flow

```bash
# 简单的工作流
main  # 始终可部署

# 创建功能分支
git checkout -b feature/new-feature main

# 提交代码
git add .
git commit -m "Add new feature"

# 推送到远程
git push origin feature/new-feature

# 创建 Pull Request
# 代码审查
# 合并到 main

# 部署
git checkout main
git pull
# 部署到生产
```

### 3. Trunk-Based Development

```bash
# 所有人直接提交到 main
# 频繁提交，小步快跑
git checkout main
git pull
# 修改代码
git add .
git commit -m "Small change"
git push

# 使用功能开关
if (featureFlags.newFeature) {
  // 新功能
}
```

## 二、高级 Git 命令

### 1. 交互式变基

```bash
# 交互式变基
git rebase -i HEAD~5

# 可用命令
# p, pick = 使用提交
# r, reword = 使用提交，但修改提交信息
# e, edit = 使用提交，但停止修改
# s, squash = 使用提交，但合并到前一个提交
# f, fixup = 类似 squash，但丢弃提交信息
# x, exec = 运行命令
# d, drop = 删除提交
```

### 2. 储藏 (Stash)

```bash
# 储藏当前工作
git stash
git stash save "Work in progress"

# 查看储藏列表
git stash list

# 应用最新储藏
git stash pop

# 应用指定储藏
git stash apply stash@{1}

# 删除储藏
git stash drop stash@{0}
git stash clear

# 创建分支从储藏
git stash branch new-branch
```

### 3. Cherry-Pick

```bash
# 拣选单个提交
git cherry-pick <commit-hash>

# 拣选多个提交
git cherry-pick <commit1> <commit2>

# 拣选范围
git cherry-pick <start>..<end>

# 拣选但不自动提交
git cherry-pick -n <commit>

# 解决冲突后继续
git cherry-pick --continue

# 中止
git cherry-pick --abort
```

### 4. Bisect

```bash
# 二分查找 bug
git bisect start
git bisect bad          # 当前版本有 bug
git bisect good v1.0   # 某个版本没有 bug

# Git 会检出中间版本
# 测试后标记
git bisect good  # 或 git bisect bad

# 找到后退出
git bisect reset

# 自动化
git bisect run npm test
```

### 5. Reflog

```bash
# 查看所有操作
git reflog

# 恢复丢失的提交
git checkout HEAD@{5}
git branch recovered-branch HEAD@{5}

# 恢复丢失的分支
git reflog
git checkout -b recovered-branch <commit-hash>
```

## 三、Git 配置

### 1. 全局配置

```bash
# 用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 编辑器
git config --global core.editor vim

# 默认分支
git config --global init.defaultBranch main

# 别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.graph 'log --graph --oneline --all'
```

### 2. 查看配置

```bash
# 查看所有配置
git config --list
git config --global --list
git config --local --list

# 查看单个配置
git config user.name
```

## 四、团队协作

### 1. Pull Request 工作流

```bash
# Fork 仓库
# 克隆你的 fork
git clone git@github.com:your-username/repo.git

# 添加上游
git remote add upstream git@github.com:original/repo.git

# 创建功能分支
git checkout -b feature/new-feature

# 提交并推送
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# 创建 Pull Request

# 同步上游
git checkout main
git pull upstream main
git push origin main

# 更新功能分支
git checkout feature/new-feature
git rebase main
git push -f origin feature/new-feature
```

### 2. 代码审查

```bash
# 检出 PR 进行本地审查
git fetch origin pull/123/head:pr-123
git checkout pr-123

# 测试后评论
```

## 五、解决冲突

### 1. 合并冲突

```bash
# 合并时冲突
git merge feature-branch
# 冲突！

# 编辑冲突文件
<<<<<<< HEAD
main 分支的内容
=======
feature 分支的内容
>>>>>>> feature-branch

# 标记解决
git add conflicted-file.txt
git commit

# 或使用工具
git mergetool
```

### 2. 变基冲突

```bash
git rebase main
# 冲突！

# 编辑冲突文件
git add conflicted-file.txt
git rebase --continue

# 或中止
git rebase --abort
```

## 六、Git 钩子

### 1. 客户端钩子

```bash
# .git/hooks/pre-commit
#!/bin/sh
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed, commit aborted"
  exit 1
fi

# .git/hooks/commit-msg
#!/bin/sh
commit_regex='^(feat|fix|docs|style|refactor|test|chore): .+'
if ! grep -qE "$commit_regex" "$1"; then
  echo "Commit message format is invalid"
  exit 1
fi
```

### 2. 使用 Husky

```bash
npm install husky --save-dev
npx husky install
npm set-script prepare "husky install"

npx husky add .husky/pre-commit "npm test"
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

## 七、大仓库管理

### 1. Git LFS

```bash
# 安装 Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.psd"
git lfs track "*.zip"
git lfs track "assets/*"

# 查看跟踪的文件
git lfs ls-files

# 克隆使用 LFS 的仓库
git lfs clone <repo-url>
```

### 2. 稀疏检出

```bash
# 稀疏检出
git init
git remote add origin <repo-url>
git config core.sparseCheckout true

echo "path/to/dir/" >> .git/info/sparse-checkout
echo "another/path/" >> .git/info/sparse-checkout

git pull origin main
```

## 八、撤销操作

### 1. 撤销工作区修改

```bash
# 撤销单个文件
git checkout -- file.txt

# 撤销所有文件
git checkout .

# 或使用 restore
git restore file.txt
git restore .
```

### 2. 撤销暂存

```bash
# 取消暂存
git reset HEAD file.txt
git restore --staged file.txt
```

### 3. 撤销提交

```bash
# 撤销最后一次提交，但保留更改
git reset --soft HEAD~1

# 撤销最后一次提交，丢弃更改
git reset --hard HEAD~1

# 创建新提交来撤销
git revert HEAD
git revert <commit-hash>
```

## 九、Git 工作技巧

### 1. 提交信息规范

```bash
# Conventional Commits
git commit -m "feat: add user login functionality"
git commit -m "fix: handle null pointer in user service"
git commit -m "docs: update API documentation"
git commit -m "style: format code with prettier"
git commit -m "refactor: simplify user authentication"
git commit -m "test: add unit tests for user service"
git commit -m "chore: update dependencies"
```

### 2. 清理历史

```bash
# 清理已合并的分支
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

# 清理远程已删除的分支
git remote prune origin
git fetch --prune
```

### 3. 快速修复

```bash
# 修改最后一次提交
git add forgotten-file.txt
git commit --amend --no-edit

# 修改提交信息
git commit --amend -m "New commit message"
```

## 十、最佳实践

1. 频繁提交，小步快跑
2. 写有意义的提交信息
3. 合理使用分支
4. 定期同步远程
5. 代码审查前自我审查
6. 使用 .gitignore
7. 不要提交敏感信息
8. 保持仓库整洁

## 十一、总结

Git 高级技巧：
- 选择合适的分支策略
- 掌握交互式变基
- 善用 stash 和 cherry-pick
- 使用 bisect 快速定位 bug
- 配置 Git 别名提高效率
- 团队协作使用 Pull Request
- 规范提交信息
- 定期清理仓库

掌握这些，让你的 Git 工作流更高效！
