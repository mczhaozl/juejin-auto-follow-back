# Shell 脚本完全指南：Bash 编程实战

> 深入讲解 Shell 脚本编程，包括变量、条件判断、循环、函数，以及实际项目中的自动化脚本编写和常见问题处理。

## 一、Shell 基础

### 1.1 首行

```bash
#!/bin/bash
# 或
#!/usr/bin/env bash
```

### 1.2 变量

```bash
# 定义变量
name="张三"
age=25

# 使用变量
echo $name
echo ${name}

# 只读变量
readonly PI=3.14

# 删除变量
unset name
```

## 二、字符串

### 2.1 引号

```bash
# 双引号 - 解析变量
name="张三"
echo "Hello $name"  # Hello 张三

# 单引号 - 原文输出
echo 'Hello $name'  # Hello $name

# 反引号 - 命令执行
date=$(date)
echo $date
```

### 2.2 字符串操作

```bash
# 拼接
str1="Hello"
str2="World"
result="${str1} ${str2}"

# 长度
${#str}

# 切片
${str:1:4}  # 从第1个字符开始，取4个

# 子串删除
${str#*.}   # 最短匹配
${str##*.}  # 最长匹配

# 子串替换
${str/old/new}   # 替换第一个
${str//old/new}  # 替换所有
```

## 三、条件判断

### 3.1 test

```bash
# 数字比较
[ $a -eq $b ]  # 等于
[ $a -ne $b ]  # 不等于
[ $a -gt $b ]  # 大于
[ $a -lt $b ]  # 小于
[ $a -ge $b ]  # 大于等于
[ $a -le $b ]  # 小于等于

# 字符串比较
[ -z $str ]    # 为空
[ -n $str ]    # 非空
[ $str1 = $str2 ]  # 相等

# 文件判断
[ -f $file ]   # 普通文件
[ -d $dir ]    # 目录
[ -e $path ]   # 存在
[ -r $file ]   # 可读
[ -w $file ]   # 可写
[ -x $file ]   # 可执行
```

### 3.2 if 语句

```bash
if [ $a -gt $b ]; then
  echo "a > b"
elif [ $a -eq $b ]; then
  echo "a = b"
else
  echo "a < b"
fi
```

### 3.3 case 语句

```bash
case $1 in
  start)
    echo "Starting..."
    ;;
  stop)
    echo "Stopping..."
    ;;
  restart)
    echo "Restarting..."
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}"
    ;;
esac
```

## 四、循环

### 4.1 for 循环

```bash
# 列表循环
for i in 1 2 3 4 5; do
  echo $i
done

# 范围循环
for i in {1..5}; do
  echo $i
done

# C 风格
for ((i=0; i<5; i++)); do
  echo $i
done

# 遍历文件
for file in *.txt; do
  echo $file
done
```

### 4.2 while 循环

```bash
# 条件循环
i=0
while [ $i -lt 5 ]; do
  echo $i
  i=$((i+1))
done

# 读取文件
while read line; do
  echo $line
done < file.txt

# 无限循环
while true; do
  echo "running..."
  sleep 1
done
```

## 五、函数

### 5.1 定义函数

```bash
# 定义
function hello() {
  echo "Hello $1"
}

# 或
hello() {
  echo "Hello $1"
}

# 调用
hello "World"
```

### 5.2 返回值

```bash
function get_sum() {
  local a=$1
  local b=$2
  echo $((a + b))
}

result=$(get_sum 10 20)
echo $result  # 30
```

## 六、数组

### 6.1 数组操作

```bash
# 定义
arr=(1 2 3 4 5)

# 访问
echo ${arr[0]}    # 第一个
echo ${arr[@]}    # 所有元素
echo ${#arr[@]}   # 长度

# 追加
arr+=(6 7)
```

### 6.2 遍历数组

```bash
for item in ${arr[@]}; do
  echo $item
done
```

## 七、实战脚本

### 7.1 备份脚本

```bash
#!/bin/bash

BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u root -p$MYSQL_PASSWORD myapp > $BACKUP_DIR/db_$DATE.sql

# 备份文件
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/myapp

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 7.2 日志分析

```bash
#!/bin/bash

LOG_FILE=$1

if [ ! -f $LOG_FILE ]; then
  echo "Log file not found"
  exit 1
fi

echo "=== 日志分析 ==="
echo "总请求数: $(wc -l < $LOG_FILE)"
echo "错误请求: $(grep 'ERROR' $LOG_FILE | wc -l)"
echo "404错误: $(grep ' 404 ' $LOG_FILE | wc -l)"
echo "IP统计:"
awk '{print $1}' $LOG_FILE | sort | uniq -c | sort -rn | head -10
```

## 八、总结

Shell 脚本核心要点：

1. **变量**：字符串、数字
2. **引号**：双引号/单引号/反引号
3. **条件**：test/[ ]
4. **循环**：for/while
5. **函数**：代码复用
6. **数组**：批量处理
7. **参数**：$1/$@

掌握这些，Shell 脚本 so easy！

---

**推荐阅读**：
- [Bash 脚本教程](https://www.shellhandbook.com/)

**如果对你有帮助，欢迎点赞收藏！**
