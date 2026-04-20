# Docker 安全最佳实践完全指南

## 一、镜像安全

### 1.1 使用官方基础镜像

```dockerfile
# Good
FROM node:20-alpine

# Bad
FROM random-image:latest
```

### 1.2 多阶段构建

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# 生产阶段
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER node
CMD ["node", "server.js"]
```

### 1.3 扫描镜像漏洞

```bash
# 使用 Trivy
trivy image myimage:latest

# 使用 Docker Scout
docker scout quickview myimage:latest
```

---

## 二、容器运行安全

### 2.1 不要使用 root 用户

```dockerfile
# 创建非 root 用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

### 2.2 只读文件系统

```bash
docker run --read-only --tmpfs /tmp --tmpfs /var/run ...
```

```yaml
# docker-compose.yml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
```

### 2.3 限制资源

```bash
docker run \
  --memory=512m \
  --memory-swap=512m \
  --cpus=1 \
  --pids-limit=100 \
  ...
```

### 2.4 丢弃权限

```bash
docker run \
  --cap-drop all \
  --cap-add NET_BIND_SERVICE \
  ...
```

---

## 三、网络安全

### 3.1 用户定义网络

```bash
# 创建隔离网络
docker network create --internal mynetwork
```

### 3.2 不要暴露所有端口

```yaml
# Good
ports:
  - "127.0.0.1:8080:80"

# Bad
ports:
  - "0.0.0.0:8080:80"
```

---

## 四、Secrets 管理

### 4.1 Docker Secrets（Swarm）

```bash
# 创建 secret
echo "mysecretpassword" | docker secret create db_password -

# 使用 secret
docker service create --secret db_password ...
```

### 4.2 不要在 Dockerfile 中硬编码

```dockerfile
# Bad
ENV API_KEY=secret123

# Good (通过运行时传递)
```

---

## 五、安全扫描

### 5.1 Dockerfile 安全检查

```bash
# 使用 Hadolint
hadolint Dockerfile

# 使用 checkov
checkov -f Dockerfile
```

### 5.2 运行时安全

```bash
# 使用 Falco
falco -r /etc/falco/falco_rules.yaml
```

---

## 六、最佳实践清单

- [ ] 使用官方或可信基础镜像
- [ ] 多阶段构建
- [ ] 定期更新基础镜像
- [ ] 扫描漏洞
- [ ] 非 root 用户
- [ ] 只读文件系统
- [ ] 限制资源
- [ ] 丢弃不必要的 capabilities
- [ ] 使用 secrets
- [ ] 网络隔离
- [ ] 日志和监控
- [ ] 签名镜像

---

## 总结

Docker 安全是多层防护的过程，从镜像、运行时、网络、secrets 等多个层面进行加固。
