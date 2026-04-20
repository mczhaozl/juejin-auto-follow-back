# CI/CD 高级实践与最佳配置完全指南：从 GitHub Actions 到 Argo CD

## 一、GitHub Actions 入门

```yaml
# .github/workflows/main.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
```

---

## 二、多环境部署

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        uses: easingthemes/ssh-deploy@v4
        with:
          SSH_PRIVATE_KEY: ${{ secrets.STAGING_SSH_KEY }}
          REMOTE_HOST: ${{ secrets.STAGING_HOST }}
          REMOTE_USER: ${{ secrets.STAGING_USER }}
          TARGET: /var/www/app

  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    needs: deploy-staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Wait for approval
        uses: andymckay/approval-action@v1
        with:
          approvers: 'admin,manager'
          
      - name: Deploy to Production
        uses: easingthemes/ssh-deploy@v4
        with:
          SSH_PRIVATE_KEY: ${{ secrets.PRODUCTION_SSH_KEY }}
          REMOTE_HOST: ${{ secrets.PRODUCTION_HOST }}
          TARGET: /var/www/app
```

---

## 三、Docker 构建与推送

```yaml
name: Build and Push

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: username/app
          tags: type=semver,pattern={{version}}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: ${{ steps.meta.outputs.tags }}
```

---

## 四、缓存优化

```yaml
- name: Cache Node.js modules
  uses: actions/cache@v3
  with:
    path: |
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

---

## 五、并行任务

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build
        run: npm run build
        
  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v3
      - name: Test
        run: npm test
        
  lint:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v3
      - name: Lint
        run: npm run lint
```

---

## 六、矩阵测试

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
        os: [ubuntu-latest, windows-latest]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
      
      - name: Test
        run: npm test
```

---

## 七、环境变量与 Secrets

```yaml
name: CI

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      API_URL: https://api.example.com
      
    steps:
      - uses: actions/checkout@v3
      
      - name: Build
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: npm run build
```

---

## 八、GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: node:18
  script:
    - npm ci
    - npm test
  cache:
    paths:
      - node_modules

build:
  stage: build
  image: node:18
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - apk add openssh
    - scp -r dist/* user@server:/var/www/app
  only:
    - main
```

---

## 九、Argo CD 持续部署

```yaml
# argocd/Application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/username/my-app.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## 十、最佳实践

1. 使用多阶段构建减少镜像大小
2. 缓存依赖加速构建
3. 并行任务提高效率
4. 使用环境变量管理配置
5. 自动化测试保证质量

---

## 十一、总结

CI/CD 是现代开发不可或缺的一部分，合理配置能极大提高开发效率。
