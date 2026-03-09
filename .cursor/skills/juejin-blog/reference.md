# 掘金博客参考：标题、摘要与示例

## 选题专家 - 标题示例

### 好的标题（有关键词、有角度）

- `Vite 5 项目里用 SVG 组件化：从导入到按需打包`（技术 + 场景 + 结果）
- `useEffect 依赖没写对？一份「闭包 + 依赖」避坑清单`（问题 + 形式）
- `从 0 搭一个带鉴权的 Node 小接口（Express + JWT）`（从 0 + 技术栈 + 目标）

### 避免的标题

- `超级好用的前端技巧`（无关键词、无信息）
- `震惊！Vue 3 竟然……`（标题党）
- `关于前端性能优化的一些想法`（过宽、无角度）

---

## 内容专家 - 摘要示例

**平台限制**：掘金摘要（brief_content）**不得超过 100 个字符**，否则发布接口会报「参数错误」。撰写时请控制在一句话内、≤100 字符。

- 教程类：`本文用 Express + JWT 从零实现登录与鉴权，包含请求拦截与 token 刷新，可直接套进现有 Node 项目。`
- 避坑类：`总结了在 React 里用 useEffect 时依赖项与闭包的常见问题，并给出对应写法与推荐实践。`
- 方案类：`对比了三种 SVG 在前端项目中的用法，最终采用 Vite + vite-plugin-svg-icons 做按需引用与打包优化。`

---

## 风格专家 - 标签建议

按技术栈与主题选 3–5 个，例如：

- 前端：`Vue`、`React`、`Vite`、`TypeScript`、`前端工程化`
- 后端：`Node.js`、`Express`、`Java`、`Go`
- 通用：`性能优化`、`最佳实践`、`源码解读`、`实战`

---

## 最小完整示例（结构）

```markdown
# 在 Vite 里把 SVG 当组件用：从导入到按需打包

> 用 vite-plugin-svg-icons + 简单封装，实现 SVG 按需引入和组件化使用，并控制打包体积。

## 一、为什么要把 SVG 组件化

- 图标多时单文件过大
- 希望按需加载、命名清晰

## 二、方案对比（简要）

- 直接 img：简单但不好改颜色
- 内联 SVG：灵活但难维护
- 选型：vite-plugin-svg-icons + 封装成 Vue/React 组件

## 三、实现步骤

### 1. 安装与配置

\`\`\`bash
pnpm add vite-plugin-svg-icons -D
\`\`\`

### 2. 封装 Icon 组件（示例）

（此处为代码块 + 简短说明）

## 四、效果与注意点

- 打包只含用到的图标
- 注意 symbolId 与文件名一致

## 总结

- 用 vite-plugin-svg-icons 做按需
- 封装成组件统一 props（size、color）
- 新图标放目录、改 symbolId 即可
```

以上可作为「内容专家」搭骨架时的默认结构参考。

---

## 发布专家 - 分类与标签

### 分类 id（category_id，取一个）

| 分类名   | category_id           |
|----------|------------------------|
| 后端     | 6809637769959178254    |
| 前端     | 6809637767543259144    |
| Android  | 6809635626879549454    |
| iOS      | 6809635626661445640    |
| 人工智能 | 6809637773935378440    |
| 开发工具 | 6809637771511070734    |
| 代码人生 | 6809637776263217160    |
| 阅读     | 6809637772874219534    |

完整列表：`GET https://api.juejin.cn/tag_api/v1/query_category_briefs`

### 标签 id（tag_ids，至少一个，建议 1–5 个）

按关键词搜索标签（取返回的 `tag_id`）：
- 接口：`POST https://api.juejin.cn/tag_api/v1/query_tag_list`
- 请求体：`{ "key_word": "关键词", "limit": 10 }`（key_word 模糊匹配 tag_name / tag_alias）

常见标签示例（id 可能随平台更新，以接口为准）：后端 6809640408797167623、前端 6809640407484334093、架构 6809640501776482317、Java 6809640445233070094、Node.js 等需用 key_word 查询后取 tag_id。

### 发布命令示例

```bash
# 先确保 cookie.txt 或 JUEJIN_COOKIE 已配置，再由发布专家根据文章内容给出下面两处 id
JUEJIN_CATEGORY_ID=6809637769959178254 JUEJIN_TAG_IDS=6809640408797167623,6809640501776482317 node scripts/juejin-save.js posts/xxx.md
# 发布
PUBLISH=1 JUEJIN_CATEGORY_ID=6809637769959178254 JUEJIN_TAG_IDS=6809640408797167623,6809640501776482317 node scripts/juejin-save.js posts/xxx.md
```

