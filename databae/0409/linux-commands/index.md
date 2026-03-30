# Linux 常用命令实战：系统管理与Shell编程指南

> 全面汇总 Linux 常用命令，包括文件操作、进程管理、网络工具、文本处理，以及 Shell 脚本编写技巧。

## 一、文件操作

### 1.1 基础命令

```bash
# 查看文件
ls -la
ls -lh

# 切换目录
cd /path/to/dir
cd ..  # 上一级
cd ~    # 家目录

# 创建
mkdir -p dir1/dir2  # 递归创建
touch file.txt

# 删除
rm file.txt
rm -rf dir/  # 强制递归删除

# 复制/移动
cp source dest
mv old new

# 查看文件内容
cat file.txt
head -n 10 file.txt
tail -n 10 file.txt
tail -f log.txt  # 实时查看
```

### 1.2 查找文件

```bash
# 按名称
find / -name "*.log"

# 按类型
find / -type f  # 文件
find / -type d  # 目录

# 按大小
find / -size +100M

# 按时间
find / -mtime -7  # 7天内修改
```

## 二、进程管理

### 2.1 查看进程

```bash
# 查看所有进程
ps aux
ps -ef

# 实时监控
top
htop

# 按 CPU/内存排序
top -o %CPU
top -o %MEM
```

### 2.2 管理进程

```bash
# 终止进程
kill PID
kill -9 PID  # 强制终止

# 按名称终止
pkill process_name

# 后台运行
nohup command &
```

## 三、网络命令

### 3.1 连接测试

```bash
# ping
ping -c 4 google.com

# 端口检测
nc -zv localhost 8080
telnet localhost 8080

# DNS 查询
dig example.com
nslookup example.com
```

### 3.2 网络工具

```bash
# 查看端口
netstat -tulpn
ss -tulpn

# 查看网络连接
curl -v https://api.example.com
wget https://example.com/file

# 传输文件
scp file.txt user@server:/path/
rsync -avz source/ dest/
```

## 四、文本处理

### 4.1 grep 家族

```bash
# 查找内容
grep "keyword" file.txt
grep -r "keyword" dir/

# 查找行号
grep -n "keyword" file.txt

# 反向匹配
grep -v "keyword" file.txt

# 正则匹配
grep -E "^[0-9]+" file.txt
```

### 4.2 awk

```bash
# 打印列
awk '{print $1}' file.txt

# 条件过滤
awk '$3 > 100' file.txt

# 格式化
awk '{printf "%-10s %d\n", $1, $2}' file.txt
```

### 4.3 sed

```bash
# 替换
sed 's/old/new/g' file.txt

# 删除行
sed '/keyword/d' file.txt

# 插入
sed -i '1i\Header' file.txt
```

## 五、压缩解压

```bash
# tar
tar -cvf archive.tar dir/
tar -xvf archive.tar
tar -cvzf archive.tar.gz dir/
tar -xvzf archive.tar.gz

# zip
zip -r archive.zip dir/
unzip archive.zip
```

## 六、权限管理

### 6.1 chmod

```bash
# 数字权限
chmod 755 file.sh
# r=4, w=2, x=1

# 符号权限
chmod +x file.sh
chmod u=rwx,go=rx file.sh
```

### 6.2 chown

```bash
chown user:group file.txt
chown -R user:group dir/
```

## 七、磁盘管理

```bash
# 查看磁盘
df -h
du -sh dir/

# 挂载
mount /dev/sdb1 /mnt/usb
umount /mnt/usb
```

## 八、Shell 脚本

### 8.1 基础语法

```bash
#!/bin/bash

name="ZhangSan"
echo "Hello, $name"

# 条件
if [ $age -gt 18 ]; then
    echo "Adult"
fi

# 循环
for i in {1..5}; do
    echo $i
done

# 函数
function greet() {
    echo "Hello, $1"
}
greet "World"
```

### 8.2 常用模板

```bash
#!/bin/bash

# 检查参数
if [ $# -eq 0 ]; then
    echo "Usage: $0 <arg>"
    exit 1
fi

# 日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理
set -e
trap 'echo "Error on line $LINENO"' ERR
```

## 九、总结

Linux 核心命令：

1. **文件操作**：ls、cp、mv、rm、find
2. **进程管理**：ps、top、kill
3. **网络工具**：curl、wget、netstat
4. **文本处理**：grep、awk、sed
5. **Shell 脚本**：条件、循环、函数

掌握这些，Linux 使用不再难！

---

**推荐阅读**：
- [Linux Command Library](https://linuxcommand.org/)
- [Bash 脚本教程](https://www.shellcheck.net/)

**如果对你有帮助，欢迎点赞收藏！**
