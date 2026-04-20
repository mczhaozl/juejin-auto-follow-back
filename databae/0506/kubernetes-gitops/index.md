# Kubernetes GitOps 完全指南

## 一、Flux CD 安装

```bash
# 安装 Flux CLI
brew install fluxcd/tap/flux

# 检查
flux check --pre

# 安装到集群
flux install
```

## 二、Git 仓库配置

```yaml
# kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: my-app
  path: "./deploy"
  prune: true
```

```yaml
# gitrepository.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/your-org/my-app
  ref:
    branch: main
```

## 三、Kustomize 配置

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml

namespace: my-app
```

## 四、Argo CD

```yaml
# application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/my-app
    targetRevision: HEAD
    path: deploy
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 五、GitOps 工作流

```bash
# 1. 修改代码
git checkout -b feature/new-feature

# 2. 提交和 PR
git add .
git commit -m "feat: new feature"
git push origin feature/new-feature

# 3. PR 合并
# Flux/ArgoCD 自动同步到集群
```

## 六、最佳实践

- 代码与清单分离仓库
- 使用分支策略管理环境
- 代码评审确保清单质量
- 定期同步和验证
- 监控同步状态
- 保存历史和审计
- 使用 Kustomize/Helm 管理配置
