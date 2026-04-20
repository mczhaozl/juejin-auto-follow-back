# Docker 网络与存储完全指南：从 bridge 到 overlay 网络

## 一、Docker 网络概述

### 1.1 网络驱动

- **bridge**：默认网络（单主机）
- **host**：使用主机网络
- **overlay**：跨主机网络（Swarm）
- **macvlan**：MAC 地址分配
- **none**：无网络

### 1.2 网络命名空间

Docker 使用 Linux 网络命名空间实现网络隔离。

---

## 二、Bridge 网络

### 2.1 默认 bridge

```bash
# 查看网络
docker network ls

# 查看 bridge 详情
docker network inspect bridge
```

### 2.2 自定义 bridge

```bash
# 创建网络
docker network create my-network

# 使用网络启动容器
docker run -d --name web --network my-network nginx
docker run -d --name db --network my-network postgres

# 容器间通信
docker exec -it web ping db
```

### 2.3 端口映射

```bash
# 主机端口:容器端口
docker run -d -p 8080:80 nginx

# 指定 IP
docker run -d -p 127.0.0.1:8080:80 nginx

# UDP 端口
docker run -d -p 53:53/udp dnsmasq

# 随机端口
docker run -d -P nginx
```

---

## 三、Host 网络

```bash
# 使用主机网络栈
docker run -d --network host nginx

# 容器直接使用主机端口
```

---

## 四、Overlay 网络

### 4.1 Swarm 模式

```bash
# 初始化 Swarm
docker swarm init --advertise-addr <manager-ip>

# 创建 overlay 网络
docker network create -d overlay my-overlay

# 创建服务
docker service create --name web --network my-overlay nginx
docker service create --name db --network my-overlay postgres
```

### 4.2 跨主机通信

```bash
# 节点 1
docker swarm init --advertise-addr 192.168.1.10

# 节点 2
docker swarm join --token <worker-token> 192.168.1.10:2377

# 创建 overlay 网络
docker network create -d overlay app-net

# 部署服务
docker service create --name web --network app-net --replicas 3 nginx
```

---

## 五、Docker 存储

### 5.1 Volume

```bash
# 创建 volume
docker volume create my-data

# 使用 volume
docker run -d -v my-data:/data postgres

# 查看 volumes
docker volume ls
docker volume inspect my-data

# 删除 volume
docker volume rm my-data
```

### 5.2 Bind Mount

```bash
# 绑定挂载主机目录
docker run -d -v /host/path:/container/path nginx

# 只读挂载
docker run -d -v /host/path:/container/path:ro nginx

# 使用相对路径
docker run -d -v $(pwd)/data:/data nginx
```

### 5.3 tmpfs 挂载

```bash
# 内存挂载
docker run -d --tmpfs /tmp nginx

# 自定义大小
docker run -d --tmpfs /tmp:rw,size=100m nginx
```

---

## 六、Docker Compose

### 6.1 网络配置

```yaml
version: '3.8'
services:
  web:
    image: nginx
    networks:
      - front-tier
      - back-tier
  
  api:
    image: my-api
    networks:
      - back-tier
  
  db:
    image: postgres
    networks:
      - back-tier
    volumes:
      - db-data:/var/lib/postgresql/data

networks:
  front-tier:
  back-tier:

volumes:
  db-data:
```

### 6.2 Volume 配置

```yaml
version: '3.8'
services:
  db:
    image: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d
      - ./config:/etc/postgresql:ro

volumes:
  postgres-data:
    driver: local
```

---

## 七、网络排错

### 7.1 查看网络

```bash
# 查看网络
docker network ls

# 查看网络详情
docker network inspect <network-name>

# 查看容器网络
docker inspect <container-name> | grep Network
```

### 7.2 连接调试

```bash
# 进入容器
docker exec -it <container> sh

# 测试连接
ping <other-container>
curl http://<service>

# 查看端口
netstat -tlnp
```

---

## 八、最佳实践

### 8.1 网络隔离

- 使用自定义 network
- 按应用分层（front-tier、back-tier）
- 限制端口暴露

### 8.2 数据持久化

- 使用 volume 存储数据
- bind mount 用于配置
- 定期备份 volume

### 8.3 安全建议

- 不使用 host 网络
- 限制容器权限
- 使用非 root 用户

---

## 总结

Docker 网络和存储是容器化应用的重要组成部分。通过合理使用不同的网络驱动和存储方式，可以构建安全、可靠的容器化服务。
