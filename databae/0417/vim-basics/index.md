# Vim 完全指南：编辑器之神实战技巧

> 深入讲解 Vim 编辑器，包括模式切换、快捷键、搜索替换、宏录制，以及实际项目中的高效编辑技巧和工作流优化。

## 一、Vim 模式

### 1.1 模式种类

```
┌─────────────────────────────────────────────────────────────┐
│                      Vim 模式                               │
│                                                              │
│  Normal (普通模式) ───── Esc ───► 移动、删除、复制         │
│       │                                                      │
│       │ i/a/o                                               │
│       ▼                                                      │
│  Insert (插入模式) ──── Esc ───► 输入文字                   │
│                                                              │
│       │ v                                                   │
│       ▼                                                      │
│  Visual (可视模式) ──── Esc ───► 选择文本                   │
│                                                              │
│       │ :                                                   │
│       ▼                                                      │
│  Command (命令模式) ──── Esc ───► 执行命令                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 切换

```vim
i       " 进入插入模式（光标前）
a       " 进入插入模式（光标后）
o       " 新建下一行并进入插入模式
O       " 新建上一行并进入插入模式

v       " 可视模式
V       " 可视行模式
Ctrl+v  " 可视块模式

:       " 命令模式
```

## 二、基础操作

### 2.1 移动

```vim
h j k l       " 左下上右
w             " 下一个词
b             " 上一个词
0             " 行首
$             " 行尾
gg            " 文件开头
G             " 文件末尾
:n            " 第 n 行

Ctrl+u        " 上半页
Ctrl+d        " 下半页
```

### 2.2 编辑

```vim
x             " 删除字符
dd            " 删除行
dw            " 删除词
d$            " 删除到行尾
d0            " 删除到行首

yy            " 复制行
yw            " 复制词
y$            " 复制到行尾

p             " 粘贴
P             " 粘贴到光标前

u             " 撤销
Ctrl+r        " 重做
```

### 2.3 快速修改

```vim
r             " 替换单个字符
R             " 替换模式
c              " 修改
cc            " 修改整行
cw            " 修改词
c$            " 修改到行尾
```

## 三、搜索替换

### 3.1 搜索

```vim
/string        " 向下搜索
?string        " 向上搜索
n              " 下一个
N              " 上一个

*              " 搜索当前词（向下）
#              " 搜索当前词（向上）
```

### 3.2 替换

```vim
:s/old/new           " 替换当前行第一个
:s/old/new/g         " 替换当前行所有
:%s/old/new/g        " 替换文件所有
:%s/old/new/gc       " 替换所有（确认）

:n,m s/old/new/g     " 替换 n 到 m 行
```

### 3.3 正则替换

```vim
:%s/(\d+)/[$1]/g     " 数字加括号
:%s/word/\U&/g       " 转大写
:%s/word/\L&/g       " 转小写
```

## 四、宏录制

### 4.1 录制宏

```vim
qa             " 开始录制到寄存器 a
... 操作 ...
q              " 停止录制

@a             " 执行宏 a
@@             " 重复上次宏
```

### 4.2 批量操作

```vim
:%normal @a    " 对所有行执行宏 a
:g/pattern/d  " 删除匹配行
:g/pattern/norm @a " 对匹配行执行宏
```

## 五、窗口与标签

### 5.1 窗口操作

```vim
:sp            " 水平分割
:vsp           " 垂直分割
Ctrl+w h/j/k/l " 切换窗口
:q             " 关闭窗口
:only          " 关闭其他
```

### 5.2 标签页

```vim
:tabnew        " 新建标签
:tabe file     " 新建标签打开文件
gt             " 下一个标签
gT             " 上一个标签
:tabc          " 关闭标签
```

## 六、实用技巧

### 6.1 快速注释

```vim
Ctrl+v         " 进入可视块模式
I              " 插入模式
//             " 输入注释符
Esc            " 退出
```

### 6.2 代码缩进

```vim
=              " 自动缩进
==             " 当前行缩进
<              " 左缩进
>              " 右缩进
```

### 6.3 文件操作

```vim
:w             " 保存
:q             " 退出
:wq            " 保存退出
:q!            " 不保存退出
:e file        " 打开文件
```

## 七、配置

### 7.1 .vimrc

```vim
" 基本设置
set nu
set relativenumber
set tabstop=2
set shiftwidth=2
set expandtab
set autoindent
set smartindent

" 搜索设置
set ignorecase
set smartcase
set incsearch

" 外观
syntax on
colorscheme gruvbox

" 快捷键
nnoremap <leader>w :w<CR>
nnoremap <leader>q :q<CR>
```

### 7.2 插件管理器

```bash
# Vim Plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

```vim
call plug#begin('~/.vim/plugged')
Plug 'preservim/nerdtree'
Plug 'vim-airline/vim-airline'
call plug#end()
```

## 八、总结

Vim 核心要点：

1. **模式**：Normal/Insert/Visual
2. **移动**：h/j/k/l/w/b
3. **编辑**：d/y/p/x
4. **搜索**：/ ? n N
5. **替换**：:s
6. **宏**：q 录制 @ 执行
7. **窗口**：:sp :vsp

掌握这些，编辑器之神就是你！

---

**推荐阅读**：
- [Vim Cheat Sheet](https://vim.rtorr.com/)
- [Practical Vim](https://book.douban.com/subject/10572062/)

**如果对你有帮助，欢迎点赞收藏！**
