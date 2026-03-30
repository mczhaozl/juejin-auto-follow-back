# Shell 脚本编程完全指南：Linux 命令行实战

> 全面介绍 Shell 脚本编程，包括变量、循环、条件判断、函数，以及实际工作中的自动化脚本案例。

## 一、基础语法

### 1.1 变量

```bash
# 定义变量（不能有空格）
name="张三"
age=25

# 使用变量
echo $name
echo ${name}

# 只读变量
readonly PI=3.14159

# 删除变量
unset name
```

### 1.2 字符串

```bash
# 单引号 - 原样输出
str='Hello $name'  # 输出: Hello $name

# 双引号 - 变量替换
str="Hello $name"  # 输出: Hello 张三

# 字符串拼接
greeting="Hello, "$name"!"
```

### 1.3 数组

```bash
# 定义数组
arr=(1 2 3 4 5)

# 访问元素
echo ${arr[0]}  # 1
echo ${arr[@]}  # 1 2 3 4 5

# 数组长度
echo ${#arr[@]}  # 5
```

## 二、条件判断

### 2.1 条件语法

```bash
# 基本 if
if [ $age -ge 18 ]; then
    echo "成年"
fi

# if-else
if [ $age -ge 18 ]; then
    echo "成年"
else
    echo "未成年"
fi

# elif
if [ $score -ge 90 ]; then
    echo "A"
elif [ $score -ge 80 ]; then
    echo "B"
else
    echo "C"
fi
```

### 2.2 比较运算符

| 运算符 | 说明 |
|--------|------|
| -eq | 等于 |
| -ne | 不等于 |
| -gt | 大于 |
| -ge | 大于等于 |
| -lt | 小于 |
| -le | 小于等于 |

### 2.3 文件判断

```bash
# 文件存在
if [ -f file.txt ]; then
    echo "文件存在"
fi

# 目录存在
if [ -d /path ]; then
    echo "目录存在"
fi

# 文件可读/可写/可执行
if [ -r file ]; then echo "可读"; fi
if [ -w file ]; then echo "可写"; fi
if [ -x file ]; then echo "可执行"; fi
```

## 三、循环

### 3.1 for 循环

```bash
# 基本 for
for i in 1 2 3 4 5; do
    echo $i
done

# 范围
for i in {1..5}; do
    echo $i
done

# C 风格
for ((i=0; i<5; i++)); do
    echo $i
done
```

### 3.2 while 循环

```bash
# 条件循环
count=0
while [ $count -lt 5 ]; do
    echo $count
    count=$((count + 1))
done

# 读取文件
while read line; do
    echo $line
done < file.txt
```

### 3.3 until

```bash
count=0
until [ $count -ge 5 ]; do
    echo $count
    count=$((count + 1))
done
```

## 四、函数

### 4.1 定义函数

```bash
# 基本函数
function greet() {
    echo "Hello, $1!"
}

# 调用
greet "张三"  # 输出: Hello, 张三!

# 返回值
function add() {
    return $(($1 + $2))
}

add 3 5
echo $?  # 输出: 8
```

### 4.2 作用域

```bash
# 全局变量
var="global"

function test() {
    # 局部变量
    local local_var="local"
    var="modified"
}

test
echo $var  # 输出: modified
```

## 五、实战案例

### 5.1 批量重命名

```bash
#!/bin/bash

for file in *.txt; do
    mv "$file" "new_$file"
done
```

### 5.2 日志分析

```bash
#!/bin/bash

# 统计 IP 访问
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10
```

### 5.3 备份脚本

```bash
#!/bin/bash

BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d)

# 创建备份
tar -czf ${BACKUP_DIR}/backup_${DATE}.tar.gz /var/www/html

# 删除 7 天前的备份
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: backup_${DATE}.tar.gz"
```

### 5.4 系统监控

```bash
#!/bin/bash

# CPU 使用率
cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# 内存使用
mem=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100)}')

# 磁盘使用
disk=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)

echo "CPU: ${cpu}%"
echo "内存: ${mem}%"
echo "磁盘: ${disk}%"
```

## 六、常用命令

### 6.1 文本处理

```bash
# awk
awk '{print $1, $3}' file.txt

# sed
sed 's/old/new/g' file.txt

# grep
grep "pattern" file.txt

# sort
sort file.txt

# uniq
uniq -c file.txt
```

### 6.2 管道和重定向

```bash
# 管道
cat file.txt | grep "pattern"

# 输出重定向
echo "hello" > file.txt
echo "hello" >> file.txt

# 错误重定向
command 2> error.log

# 管道符
command1 | command2 | command3
```

## 七、总结

Shell 脚本核心要点：

1. **变量**：定义和使用
2. **字符串**：单引号、双引号
3. **条件**：if/elif/else
4. **循环**：for/while/until
5. **函数**：定义和调用
6. **文本处理**：awk/sed/grep
7. **管道**：命令组合

掌握这些，Shell 脚本不再难！

---

**推荐阅读**：
- [Bash 官方文档](https://www.gnu.org/software/bash/manual/)
- [Shell 脚本教程](https://www.shellhandbook.com/)

**如果对你有帮助，欢迎点赞收藏！**
