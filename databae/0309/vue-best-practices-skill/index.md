# Vue Best Practices Skill 推荐

> 整理在 Vue 项目里能直接提升可维护性与协作效率的实践与「技能」：从组合式 API、类型到目录与规范，方便团队统一风格、少踩坑。

---

## 一、组合式 API 与逻辑复用

- **优先用 `<script setup>`**：少一层 return，类型推断更好，和 Composition API 天然契合。
- **逻辑抽成 composables**：把「请求列表」「表单校验」「弹窗开关」等抽成 `useXxx`，便于在多个页面复用和单测。
- **避免在 setup 里写过长逻辑**：超过几十行就考虑拆成 composable 或子模块，保持单文件可读。

---

## 二、类型与规范

- **TypeScript 尽量跟上**：哪怕先给 props、emits 和 composable 的入参/返回值加类型，也能减少运行时错误。
- **Props 用 defineProps 且只读**：不要直接改 props，需要「派生状态」用 computed，需要「改完回传」用 v-model 或 emit。
- **Emits 用 defineEmits 声明**：方便类型推导和文档化，例如 `defineEmits<{ submit: [payload: FormPayload] }>()`。

---

## 三、目录与文件组织

- **按功能/业务划分目录**：例如 `views/order/`、`components/order/`，而不是按「所有组件一个夹」。
- **组件命名**：多词、见名知意（如 `OrderCard.vue`、`UserAvatar.vue`），避免与原生标签撞名。
- **样式**：优先 scoped；如需统一设计，用 CSS 变量或主题文件，少写魔法数字。

---

## 四、性能与体验

- **大列表用虚拟滚动**：表格、长列表用 `vue-virtual-scroller` 或类似方案，避免一次渲染成千上万个节点。
- **路由级懒加载**：`component: () => import('@/views/xxx.vue')`，减小首屏包体积。
- **按需引入 UI 库**：能按需就按需，避免全量引入。

---

## 五、Skill 推荐（可沉淀为团队规范）

把上述实践整理成「团队 Skill」或文档，新人按同一套来写，能少很多分歧：

- **命名**：组件 PascalCase、文件 kebab-case 或 PascalCase 与团队约定一致。
- **单文件结构**：template → script → style；script 里顺序可约定为 imports → props/emits → composables → 本地状态。
- **提交前**：跑一遍 ESLint + 类型检查，必要时加简单的 E2E 或快照，防止改坏公共组件。

---

## 总结

- Vue 项目里：组合式 API + composables、TypeScript、清晰的目录与命名，是性价比最高的「Best Practices」。
- 把常用约定写成 Skill/文档，便于每天自动上传、团队统一执行；再配合懒加载与虚拟列表，兼顾可维护性和性能。

若对你有用，欢迎点赞、收藏；你们团队有别的 Vue 实践或 Skill 清单，也欢迎在评论区分享。
