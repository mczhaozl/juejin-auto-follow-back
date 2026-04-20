# Docker Registry 与镜像管理完全指南

## 一、Registry 概述

### 1.1 什么是 Registry

存储和分发 Docker 镜像的服务。

### 1.2 常见 Registry

- Docker Hub
- GitHub Container Registry (GHCR)
- AWS ECR
- Harbor
- 私有 Registry

---

## 二、部署私有 Registry

### 2.1 使用 Docker 官方 Registry

```yaml
# docker-compose.yml
version: '3'
services:
  registry:
    image: registry:2
    ports:
      - 5000:5000
    volumes:
      - ./data:/var/lib/registry
      - ./config.yml:/etc/docker/registry/config.yml
```

```yaml
# config.yml
version: 0.1
log:
  level: info
storage:
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: 0.0.0.0:5000
```

```bash
docker-compose up -d
```

---

## 三、基本操作

```bash
# 标记镜像
docker tag myimage localhost:5000/myimage:v1

# 推送镜像
docker push localhost:5000/myimage:v1

# 拉取镜像
docker pull localhost:5000/myimage:v1

# 查看仓库
curl http://localhost:5000/v2/_catalog

# 查看标签
curl http://localhost:5000/v2/myimage/tags/list
```

---

## 四、安全配置

### 4.1 TLS

```yaml
services:
  registry:
    image: registry:2
    ports:
      - 5000:5000
    volumes:
      - ./certs:/certs
    environment:
      REGISTRY_HTTP_TLS_CERTIFICATE: /certs/domain.crt
      REGISTRY_HTTP_TLS_KEY: /certs/domain.key
```

### 4.2 认证

```yaml
services:
  registry:
    image: registry:2
    environment:
      REGISTRY_AUTH: htpasswd
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd
      REGISTRY_AUTH_HTPASSWD_REALM: Registry Realm
    volumes:
      - ./auth:/auth
```

```bash
# 创建用户
docker run --rm --entrypoint htpasswd httpd:2 -Bbn user password > ./auth/htpasswd
docker login localhost:5000
```

---

## 五、存储

### 5.1 本地存储

```yaml
storage:
  filesystem:
    rootdirectory: /var/lib/registry
```

### 5.2 S3 存储

```yaml
storage:
  s3:
    accesskey: AKIAxxx
    secretkey: secret
    region: us-east-1
    bucket: my-registry
```

---

## 六、镜像管理

### 6.1 删除镜像

```bash
# 获取 digest
curl --header "Accept: application/vnd.docker.distribution.manifest.v2+json" \
  http://localhost:5000/v2/myimage/manifests/latest \
  -v

# 删除
curl -X DELETE \
  http://localhost:5000/v2/myimage/manifests/sha256:xxx

# 垃圾回收
docker exec -it registry /bin/registry garbage-collect /etc/docker/registry/config.yml
```

---

## 七、企业级方案：Harbor

```yaml
# docker-compose.yml
version: '2'
services:
  harbor:
    image: goharbor/harbor-core:latest
    # ... Harbor 配置
```

```bash
# 下载 Harbor
wget https://github.com/goharbor/harbor/releases/download/v2.0.0/harbor-online-installer-v2.0.0.tgz
tar xzf harbor-online-installer-v2.0.0.tgz
cd harbor

# 配置 install.sh
./install.sh
```

---

## 八、最佳实践

- 配置 TLS
- 设置认证
- 定期备份
- 清理旧镜像
- 监控存储使用

---

## 总结

私有 Registry 提供了镜像管理的灵活性，通过合理配置可以满足企业级需求。
