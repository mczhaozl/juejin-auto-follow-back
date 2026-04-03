# Git 高级技巧完全指南

Git 是最流行的版本控制系统。本文将带你从基础到高级，全面掌握 Git 的高级技巧。

## 一、Git 基础回顾

### 1. 常用命令

```bash
# 初始化仓库
git init

# 克隆仓库
git clone https://github.com/user/repo.git

# 查看状态
git status

# 添加文件
git add .
git add file.txt

# 提交
git commit -m "commit message"

# 查看日志
git log
git log --oneline
git log --graph --oneline --all

# 查看差异
git diff
git diff --staged

# 分支
git branch
git branch feature
git checkout feature
git switch feature
git checkout -b feature
git branch -d feature

# 合并
git merge feature
git rebase main

# 推送和拉取
git push origin main
git pull origin main
git fetch origin
```

### 2. Git 工作流

```
工作区 → 暂存区 → 本地仓库 → 远程仓库

git add        git commit        git push
```

## 二、Git 高级技巧

### 1. 交互式 rebase

```bash
# 交互式 rebase
git rebase -i HEAD~5

# 命令:
# p, pick = 使用提交
# r, reword = 使用提交，但修改提交信息
# e, edit = 使用提交，但停止修改
# s, squash = 使用提交，但合并到前一个提交
# f, fixup = 类似 squash，但丢弃提交信息
# d, drop = 删除提交
```

```bash
# 示例：合并最后 3 个提交
git rebase -i HEAD~3

# 在编辑器中修改为:
pick abc123 First commit
squash def456 Second commit
squash ghi789 Third commit
```

### 2. 修改提交

```bash
# 修改最后一次提交
git commit --amend
git commit --amend --no-edit

# 修改已推送的提交（谨慎使用！）
git commit --amend
git push --force-with-lease

# 撤销提交但保留更改
git reset --soft HEAD~1

# 撤销提交并丢弃更改
git reset --hard HEAD~1

# 撤销工作区更改
git checkout -- file.txt
git restore file.txt

# 撤销暂存
git reset HEAD file.txt
git restore --staged file.txt
```

### 3. Cherry-pick

```bash
# 应用单个提交
git cherry-pick abc123

# 应用多个提交
git cherry-pick abc123 def456

# 应用范围内的提交
git cherry-pick abc123..ghi789

# 应用提交但不自动提交
git cherry-pick -n abc123

# 编辑提交信息
git cherry-pick -e abc123

# 继续 cherry-pick（解决冲突后）
git cherry-pick --continue

# 跳过冲突的提交
git cherry-pick --skip

# 中止 cherry-pick
git cherry-pick --abort
```

### 4. Bisect（二分查找）

```bash
# 开始 bisect
git bisect start

# 标记当前提交为 bad
git bisect bad

# 标记已知的 good 提交
git bisect good v1.0

# Git 会自动切换到中间提交
# 测试后标记:
git bisect good
# 或
git bisect bad

# 找到第一个 bad 提交后，查看结果
git bisect log

# 退出 bisect
git bisect reset

# 自动化 bisect
git bisect start HEAD v1.0
git bisect run npm test
```

### 5. Stash（暂存）

```bash
# 暂存更改
git stash
git stash save "message"

# 查看暂存列表
git stash list

# 应用最新暂存
git stash pop
git stash apply

# 应用特定暂存
git stash pop stash@{1}
git stash apply stash@{1}

# 查看暂存内容
git stash show
git stash show -p stash@{1}

# 删除暂存
git stash drop stash@{1}
git stash clear

# 创建分支从暂存
git stash branch new-branch stash@{1}
```

### 6. Worktree（工作树）

```bash
# 创建新的工作树
git worktree add ../feature-branch feature

# 查看工作树
git worktree list

# 删除工作树
git worktree remove ../feature-branch

# 清理已删除的工作树
git worktree prune
```

### 7. Reflog（引用日志）

```bash
# 查看 reflog
git reflog

# 恢复丢失的提交
git reset --hard HEAD@{5}

# 查看分支 reflog
git reflog show main
```

### 8. Blame（查找责任人）

```bash
# 查看每一行的修改人
git blame file.txt

# 查看特定行
git blame -L 10,20 file.txt

# 显示提交哈希
git blame -l file.txt
```

### 9. Git Hooks

```bash
# 钩子位置
.git/hooks/

# 常用钩子
# pre-commit: 提交前
# pre-push: 推送前
# commit-msg: 提交信息
# post-merge: 合并后

# 示例: pre-commit
#!/bin/sh
npm run lint
if [ $? -ne 0 ]; then
  echo "Linting failed, commit aborted"
  exit 1
fi

# 使钩子可执行
chmod +x .git/hooks/pre-commit
```

## 三、Git 配置

### 1. 基础配置

```bash
# 用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 编辑器
git config --global core.editor "vim"

# 别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --graph --oneline --all"

# 查看配置
git config --list
git config --global --list

# 编辑配置文件
git config --global --edit
```

### 2. 高级配置

```bash
# 自动更正
git config --global help.autocorrect 1

# 颜色
git config --global color.ui auto

# 分支排序
git config --global branch.sort -committerdate

# 拉取时 rebase
git config --global pull.rebase true

# 默认分支名
git config --global init.defaultBranch main

# 凭据缓存
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'

# 代理
git config --global http.proxy http://proxy:8080
git config --global https.proxy https://proxy:8080
```

## 四、分支策略

### 1. Git Flow

```
master: 生产环境
develop: 开发环境
feature/*: 功能分支
release/*: 发布分支
hotfix/*: 热修复分支

# 创建功能分支
git checkout -b feature/new-feature develop

# 完成功能分支
git checkout develop
git merge --no-ff feature/new-feature
git branch -d feature/new-feature

# 创建发布分支
git checkout -b release/1.0.0 develop

# 完成发布分支
git checkout master
git merge --no-ff release/1.0.0
git tag -a v1.0.0
git checkout develop
git merge --no-ff release/1.0.0
git branch -d release/1.0.0

# 创建热修复分支
git checkout -b hotfix/1.0.1 master

# 完成热修复分支
git checkout master
git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1
git checkout develop
git merge --no-ff hotfix/1.0.1
git branch -d hotfix/1.0.1
```

### 2. GitHub Flow

```
main: 生产环境
feature/*: 功能分支

# 创建功能分支
git checkout -b feature/new-feature main

# 提交和推送
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# 创建 Pull Request
# 代码审查
# 合并到 main

# 部署到生产
```

### 3. Trunk-Based Development

```
main: 主分支
short-lived feature branches

# 创建短期分支
git checkout -b feature/task-123 main

# 频繁提交
git add .
git commit -m "WIP: Partial implementation"
git push origin feature/task-123

# 快速合并
git checkout main
git pull origin main
git merge --no-ff feature/task-123
git push origin main
git branch -d feature/task-123
```

## 五、远程仓库

### 1. 基础操作

```bash
# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 查看远程仓库
git remote -v

# 修改远程仓库
git remote set-url origin https://github.com/user/new-repo.git

# 删除远程仓库
git remote remove origin

# 重命名远程仓库
git remote rename origin upstream

# 获取远程更新
git fetch origin
git pull origin main

# 推送
git push origin main
git push origin feature

# 删除远程分支
git push origin --delete feature

# 推送标签
git push origin v1.0.0
git push origin --tags
```

### 2. Fork 和 PR 流程

```bash
# 1. Fork 仓库
# 在 GitHub 上点击 Fork 按钮

# 2. 克隆 Fork 的仓库
git clone https://github.com/your-username/repo.git
cd repo

# 3. 添加上游仓库
git remote add upstream https://github.com/original-username/repo.git

# 4. 创建功能分支
git checkout -b feature/new-feature

# 5. 提交更改
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# 6. 创建 Pull Request
# 在 GitHub 上创建 PR

# 7. 同步上游
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## 六、解决冲突

```bash
# 合并时冲突
git merge feature
# 编辑冲突文件
# 标记解决
git add .
git commit

# rebase 时冲突
git rebase main
# 编辑冲突文件
git add .
git rebase --continue

# 查看冲突
git diff

# 使用可视化工具
git mergetool

# 中止
git merge --abort
git rebase --abort
```

## 七、大文件处理

```bash
# Git LFS (Large File Storage)
git lfs install
git lfs track "*.psd"
git lfs track "*.zip"
git add .gitattributes
git add file.psd
git commit -m "Add large file"
git push
```

## 八、最佳实践

1. 写好提交信息
2. 频繁提交
3. 使用分支
4. 代码审查
5. 使用 .gitignore
6. 定期清理
7. 备份重要仓库
8. 学习 rebase
9. 使用 Git Hooks
10. 文档化工作流

```bash
# .gitignore 示例
node_modules/
.DS_Store
*.log
.env
dist/
build/
.idea/
.vscode/
*.swp
```

## 九、总结

Git 高级技巧核心要点：
- 交互式 rebase
- 修改提交
- Cherry-pick
- Bisect（二分查找）
- Stash（暂存）
- Worktree（工作树）
- Reflog（引用日志）
- Git Hooks
- 分支策略（Git Flow、GitHub Flow、Trunk-Based）
- 远程仓库
- 解决冲突
- Git LFS
- 最佳实践

开始使用 Git 高级技巧提升你的工作效率吧！
