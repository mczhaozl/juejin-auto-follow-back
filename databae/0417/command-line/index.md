# 命令行效率完全指南：终端工具与技巧

> 深入讲解命令行效率提升，包括快捷键、管道重定向、任务管理，以及实际项目中的自动化脚本和工作流优化。

## 一、快捷键

### 1.1 Bash/Zsh 快捷键

```bash
# 光标移动
Ctrl+a      # 行首
Ctrl+e      # 行尾
Ctrl+b      # 前一个字符
Ctrl+f      # 后一个字符
Alt+b       # 前一个单词
Alt+f       # 后一个单词

# 编辑
Ctrl+u      # 删除到行首
Ctrl+k      # 删除到行尾
Ctrl+w      # 删除前一个单词
Ctrl+y      # 粘贴
Ctrl+t      # 交换字符

# 历史
Ctrl+r      # 搜索历史
Ctrl+g      # 退出搜索
Ctrl+p      # 上一个命令
Ctrl+n      # 下一个命令
!!          # 上一个命令
!$          # 最后一个参数
```

### 1.2 Vim 模式

```bash
# 启用 Vi 模式
set -o vi

# Esc 进入 Normal 模式
# i 进入 Insert 模式
# / 搜索
```

## 二、管道与重定向

### 2.1 重定向

```bash
# 输出重定向
command > file      # 覆盖
command >> file    # 追加
command 2> file    # 错误重定向

# 输入重定向
command < file
command << EOF
  content
EOF

# 同时重定向
command > file 2>&1
command &> file
```

### 2.2 管道

```bash
# 基本管道
cat file | grep pattern

# 链式管道
cat log | grep ERROR | wc -l

# tee（同时输出到文件和终端）
command | tee file
```

## 三、文本处理

### 3.1 常用命令

```bash
# 统计
wc -l file         # 行数
wc -w file         # 单词数
wc -c file         # 字符数

# 排序
sort file          # 排序
sort -u file       # 去重排序
sort -k2 file      # 按第2列排序
sort -rn file      # 逆序数字排序

# 去重
uniq file          # 相邻去重
uniq -c file       # 统计重复
```

### 3.2 awk

```bash
# 打印列
awk '{print $1}' file
awk -F',' '{print $1}' file

# 条件
awk '$3 > 80 {print $1, $3}' file

# 计算
awk '{sum+=$1} END {print sum}' file
```

### 3.3 sed

```bash
# 替换
sed 's/old/new/' file
sed 's/old/new/g' file
sed -i 's/old/new/g' file

# 删除
sed '/pattern/d' file

# 行操作
sed -n '1,10p' file     # 打印1-10行
sed '1,5d' file         # 删除1-5行
```

## 四、任务管理

### 4.1 后台任务

```bash
# 后台运行
command &
jobs                # 查看任务
fg                  # 调到前台
bg                  # 后台继续
Ctrl+z              # 暂停
```

### 4.2 nohup

```bash
# 持久运行
nohup command &
nohup command > output.log 2>&1 &

# 查看进程
ps aux | grep command
```

### 4.3 screen

```bash
# 创建会话
screen -S mysession

# 退出（保持运行）
Ctrl+a d

# 恢复
screen -r mysession

# 列出
screen -ls
```

## 五、高效工具

### 5.1 tldr

```bash
# 简化 man 手册
tldr tar
tldr curl
```

### 5.2 fzf

```bash
# 模糊搜索
fzf
history | fzf

# 文件搜索
find . -name "*.js" | fzf
```

### 5.3 jq

```bash
# JSON 处理
cat data.json | jq '.key'
cat data.json | jq '.array[]'
cat data.json | jq 'map(select(.id > 10))'
```

## 六、别名与函数

### 6.1 别名

```bash
# ~/.bashrc 或 ~/.zshrc
alias ll='ls -lah'
alias la='ls -A'
alias l='ls -CF'

alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'

alias ..='cd ..'
alias ...='cd ../..'
```

### 6.2 函数

```bash
# 创建目录并进入
mkcd() {
  mkdir -p "$1" && cd "$1"
}

# 提取压缩包
extract() {
  if [ -f $1 ] ; then
    case $1 in
      *.tar.bz2) tar xjf $1 ;;
      *.tar.gz)  tar xzf $1 ;;
      *.bz2)     bunzip2 $1 ;;
      *.rar)     unrar x $1 ;;
      *.gz)      gunzip $1  ;;
      *.tar)     tar xf $1 ;;
      *.tbz2)    tar xjf $1 ;;
      *.tgz)     tar xzf $1 ;;
      *.zip)     unzip $1 ;;
      *.Z)       uncompress $1 ;;
      *)         echo "'$1' cannot be extracted" ;;
    esac
  else
    echo "'$1' is not a valid file"
  fi
}
```

## 七、实战案例

### 7.1 日志分析

```bash
# 统计错误
grep ERROR app.log | wc -l

# 按 IP 统计
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 实时监控
tail -f app.log | grep ERROR
```

### 7.2 数据处理

```bash
# CSV 处理
awk -F',' '{print $1, $3}' data.csv

# JSON 提取
cat data.json | jq '.users[].name'

# 批量重命名
for f in *.txt; do mv "$f" "${f%.txt}.md"; done
```

## 八、总结

命令行效率核心要点：

1. **快捷键**：Ctrl+r/Ctrl+a/e
2. **管道**：|
3. **重定向**：> >>
4. **文本处理**：awk/sed
5. **任务管理**：&/nohup/screen
6. **别名**：简化命令

掌握这些，效率翻倍 so easy！

---

**推荐阅读**：
- [Bash 快捷键](https://www.howtogeek.com/howto/ubuntu/keyboard-shortcuts-for-bash-command-line-for-ubuntu-debianlinux/)

**如果对你有帮助，欢迎点赞收藏！**
