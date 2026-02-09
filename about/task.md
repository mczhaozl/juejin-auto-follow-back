GitHub Actions 每月 2000 分钟免费时长，是 GitHub 免费账户给私有仓库提供的官方 CI/CD 云端运行时间额度，公共仓库不限时长。下面从是什么、有什么用、在哪用、怎么用、用量查看与注意事项完整说明。
一、2000 分钟免费时长：基本规则
适用对象：GitHub Free 个人 / 组织账户的私有仓库。
额度：每月 2000 分钟（自然月 1 号重置）。
环境：仅适用于 GitHub 标准托管运行器（Linux/Windows/macOS），不能用于大型运行器（Larger runners）。
计费系数：不同系统分钟数按不同倍率计费（实际消耗 = 运行分钟 × 系数）：
Linux：×1（最省）
Windows：×2
macOS：×10（最耗额度）
公共仓库：使用标准运行器完全免费、不限时长。
自托管运行器：不计入免费额度，完全免费。
二、GitHub Actions 有什么用？
它是 GitHub 内置的自动化工作流引擎，在云端虚拟机执行脚本，替代手动重复操作。
核心用途
CI/CD 自动化（最常用）
代码提交 / PR 时自动跑单元测试、代码检查、构建打包。
合并主分支后自动部署到服务器、Vercel、阿里云、Docker 等。
定时任务
每日 / 每周爬取数据、生成报表、发送邮件 / 钉钉 / 企业微信通知。
定时清理、备份、同步文件。
发布与维护
打 Tag 时自动生成 Release、上传安装包、更新文档。
自动更新依赖、打安全补丁、生成变更日志。
其他自动化
自动处理 Issue/PR 标签、评论、关闭。
生成静态站点、编译文档、跑脚本任务。
一句话：把所有能自动化的开发 / 运维 / 数据任务，交给云端免费执行。
三、在哪使用？
在你的 GitHub 仓库 里使用，入口在仓库顶部导航栏的 Actions 标签页。
四、怎么使用？（完整步骤）
1. 准备仓库
新建或进入一个私有仓库（公共仓库不消耗 2000 分钟额度）。
2. 创建工作流文件
在仓库根目录创建目录：.github/workflows/。
新建 YAML 文件（如 ci.yml、deploy.yml），编写工作流配置。
3. 编写最简示例（自动测试）
yaml
# .github/workflows/ci.yml
name: CI Test

# 触发条件：push 到 main 分支、提交 PR 到 main
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

# 任务
jobs:
  test:
    # 运行环境（选 Linux 最省额度）
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm install

      - name: Run tests
        run: npm test
4. 触发与查看
提交代码到 main 或发起 PR，自动触发运行。
进入仓库 → Actions 标签页，查看运行日志、成功 / 失败状态。
5. 手动触发（可选）
在 YAML 中添加 workflow_dispatch，即可在 Actions 页面手动点击运行：
yaml
on:
  workflow_dispatch: # 允许手动触发
  push: ...
五、查看用量与剩余额度
进入个人 / 组织主页 → 右上角头像 → Settings（设置）。
左侧菜单 → Billing and plans（计费与计划）。
在 GitHub Actions 区域，查看：
当月已用分钟数、剩余额度。
按仓库、按系统（Linux/Windows/macOS）的用量明细。
六、节省额度的实用技巧
优先用 Linux（系数 ×1，最划算）。
缩短运行时间：缓存依赖（actions/cache）、精简步骤、并行任务。
控制触发频率：只在关键分支 / 关键事件触发，避免频繁运行。
公共仓库不耗额度：非敏感项目设为 Public，免费无限用。
自托管运行器：用自己服务器 / PC 运行，完全不计费。
七、超出额度会怎样？
免费账户未绑卡：额度用完后，私有仓库 Actions 会被暂停，下月 1 号重置恢复。
绑卡后：超出部分按标准费率计费（Linux $0.008/分钟、Windows $0.016、macOS $0.08）。
需要我给你生成一个可直接复制的定时任务工作流模板（比如每日自动爬取数据并发邮件）吗？