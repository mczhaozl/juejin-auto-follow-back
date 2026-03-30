# Linux 命令完全指南：日常操作与系统管理

> 深入讲解 Linux 常用命令，包括文件操作、进程管理、网络配置、用户权限，以及实际项目中的系统维护和故障排查。

## 一、文件操作

### 1.1 基础命令

```bash
# 查看文件
ls -la /path           # 详细列表
ls -lh                 # 人性化大小
ls -lt                 # 按时间排序

# 切换目录
cd /path               # 切换
cd -                   # 返回上次目录
cd ~                   # 家目录
pwd                    # 当前目录

# 创建/删除
mkdir -p dir/subdir    # 递归创建
rm -rf dir             # 强制删除
touch file             # 创建空文件
cp -r src dest         # 递归复制
mv old new             # 移动/重命名
```

### 1.2 查看文件

```bash
# 查看内容
cat file               # 全部
head -n 10 file        # 前10行
tail -n 10 file        # 后10行
tail -f file           # 实时跟踪
less file              # 分页查看
wc -l file             # 行数统计

# 搜索
grep "pattern" file    # 搜索
grep -r "pattern" dir # 递归搜索
find / -name "*.log"   # 按名查找
find / -size +100M     # 按大小查找
```

## 二、进程管理

### 2.1 进程查看

```bash
# 查看进程
ps -ef                 # 详细列表
ps aux                 # BSD 格式
top                    # 实时监控
htop                   # 交互式监控
pstree                 # 进程树

# 过滤
ps -ef | grep nginx
```

### 2.2 进程控制

```bash
# 终止进程
kill PID               # 终止
kill -9 PID            # 强制终止
pkill nginx           # 按名终止

# 后台运行
./script.sh &         # 后台运行
nohup ./script.sh &   # 持久后台
ctrl+z                # 暂停
bg                    # 后台继续
fg                    # 前台继续
```

## 三、权限管理

### 3.1 权限概念

```
rwx rwx rwx
└── ┴── ┴──
    │   │
    │   └── 其他人
    └─────── 所属组
└─────────── 所有者
```

### 3.2 权限命令

```bash
# 修改权限
chmod 755 file         # 数字方式
chmod +x file          # 添加执行
chmod -R 755 dir       # 递归

# 修改所有者
chown user:group file
chown -R user:group dir
```

## 四、网络命令

### 4.1 网络查看

```bash
# IP/网络
ip addr               # IP 地址
ip link               # 网卡信息
netstat -tuln         # 监听端口
ss -tuln              # 替代 netstat

# 连通性
ping -c 4 host        # Ping 测试
curl -I url           # HTTP 请求
wget url              # 下载
```

### 4.2 SSH

```bash
# 连接
ssh user@host
ssh -p 22 user@host

# 密钥
ssh-keygen            # 生成密钥
ssh-copy-id user@host # 复制公钥
```

## 五、系统管理

### 5.1 系统信息

```bash
# 系统
uname -a              # 内核信息
cat /etc/os-release  # 发行版
uptime                # 运行时间
date                  # 时间

# 资源
df -h                 # 磁盘使用
free -h               # 内存使用
```

### 5.2 用户管理

```bash
# 用户
useradd user          # 添加用户
userdel user          # 删除用户
passwd user           # 修改密码

# 组
groupadd group        # 添加组
usermod -G group user # 加入组
```

## 六、压缩解压

### 6.1 压缩命令

```bash
# tar
tar -cvf archive.tar dir/
tar -xvf archive.tar
tar -czvf archive.tar.gz dir/
tar -xzvf archive.tar.gz

# zip
zip -r archive.zip dir/
unzip archive.zip
```

## 七、实战案例

### 7.1 日志分析

```bash
# 查看错误日志
tail -f /var/log/nginx/error.log

# 搜索错误
grep "ERROR" /var/log/app.log | tail -100

# 统计 IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```

### 7.2 系统监控

```bash
# CPU 监控
top
htop

# 磁盘监控
df -h

# 内存监控
free -h

# 网络监控
iftop
nethogs
```

## 八、总结

Linux 命令核心要点：

1. **文件操作**：ls/cd/cp/mv/rm
2. **进程**：ps/kill/top
3. **权限**：chmod/chown
4. **网络**：ping/curl/ssh
5. **系统**：df/free/uptime
6. **压缩**：tar/zip

掌握这些，Linux 操作 so easy！

---

**推荐阅读**：
- [Linux 命令大全](https://www.linuxcool.com/)

**如果对你有帮助，欢迎点赞收藏！**
