# 别再用 useState / data 管 Tabs 的 activeKey 了：和 URL 绑定才香

> Code review 发现组员用 state 管 tabs，想起自己踩过的坑。建议和 URL 绑定，方便调试和分享链接。

---

## 一、Code review 里常见写法：state 管 activeKey

很多人在写 Tabs 时，会照着**组件库的 demo** 来：用 **React 的 useState** 或 **Vue 的 data** 存当前选中的 `activeKey`，点击 tab 就 `setState` / 改 `data`。demo 里这样写没问题——只是为了演示「能切换」——但**搬到业务里就会踩坑**。

```jsx
// React：典型 demo 写法
const [activeKey, setActiveKey] = useState('1');
<Tabs activeKey={activeKey} onChange={setActiveKey}>...</Tabs>
```

```vue
<!-- Vue：典型 demo 写法 -->
<script setup>
const activeKey = ref('1');
</script>
<template>
  <Tabs v-model:activeKey="activeKey">...</Tabs>
</template>
```

看起来没问题，功能也能跑。可一旦要**调试、协作、分享**，问题就来了。

---

## 二、为啥吃亏：难调试、不能分享链接、刷新就丢

- **刷新就丢**：用户切到某个 tab 后刷新页面，又回到默认 tab，无法「停在当前 tab」。
- **链接没法用**：想把这个 tab 的页面发给同事或贴到文档里，对方打开永远是默认 tab，你没法说「看第二个 tab」。
- **调试费劲**：排查某个 tab 下的问题时，每次都要手动点过去；不能直接通过改 URL 定位到目标 tab。
- **和路由脱节**：SPA 里路由本来就能表达「当前在看什么」，tabs 却单独用 state 再记一份，状态分散、容易不一致。

这些坑我以前都踩过：改完 bug 想让同事看一眼，发个链接过去，对方打开是第一个 tab，还得口头说「你点一下第二个」；自己排查也要反复点。后来改成 **tabs 和 URL 绑定**，一下子省心很多。

---

## 三、推荐做法：和 URL 绑定

把 **当前 tab 的 key 放进 URL**（hash 或 query），用 **路由** 作为唯一数据源，tabs 只做「读 URL → 渲染 / 写 URL → 跳转」。

好处很直接：

- **可分享**：复制链接就是「当前 tab」，别人打开即同屏。
- **可调试**：改 URL 就能切 tab，不用在页面上点。
- **刷新不丢**：刷新后从 URL 恢复，始终停在当前 tab。
- **和路由统一**：一个状态源，逻辑清晰。

### 3.1 React：用 searchParams 或 hash

以 **React Router 6** 为例，用 **searchParams** 存 tab key（如 `?tab=2`）：

```jsx
import { useSearchParams } from 'react-router-dom';

function PageWithTabs() {
    const [searchParams, setSearchParams] = useSearchParams();
    const activeKey = searchParams.get('tab') || '1';

    const onChange = (key) => {
        setSearchParams({ tab: key });
    };

    return (
        <Tabs activeKey={activeKey} onChange={onChange}>
            <Tabs.TabPane key="1" tab="概览">...</Tabs.TabPane>
            <Tabs.TabPane key="2" tab="详情">...</Tabs.TabPane>
        </Tabs>
    );
}
```

若不想用 query，可以用 **hash**（如 `#tab=2`），用 `useLocation().hash` 或 `window.location.hash` 读写的思路一样：**读 URL → 给 activeKey；改 tab → 写 URL**。

### 3.2 Vue：用 query 或 hash

**Vue Router** 里用 **query** 存 tab key：

```vue
<script setup>
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const activeKey = computed(() => route.query.tab || '1');

function onChange(key) {
    router.replace({ query: { ...route.query, tab: key } });
}
</script>
<template>
    <Tabs :activeKey="activeKey" @update:activeKey="onChange">
        <Tabs.TabPane key="1" tab="概览">...</Tabs.TabPane>
        <Tabs.TabPane key="2" tab="详情">...</Tabs.TabPane>
    </Tabs>
</template>
```

同样，也可以用 **hash** 存（如 `#detail`），用 `route.hash` 读写即可。

---

## 四、小结

- **别学 demo 用 state/data 管 tabs**：只适合「演示能切换」，业务里会带来刷新丢、不能分享链接、调试麻烦。
- **把 activeKey 和 URL 绑定**：用 searchParams、query 或 hash 存当前 tab，路由即唯一数据源；方便调试、复制链接、刷新不丢。
- **Code review 时可以提一嘴**：看到 tabs 还在用 useState/data 且没有和 URL 联动时，建议改成「读 URL → 渲染，改 tab → 写 URL」，少踩坑。

如果你也经历过「发链接别人看不到当前 tab」或「调试要反复点 tab」的痛，不妨把现有页面的 tabs 改成和 URL 绑定，体验会明显好一截。觉得有用欢迎点赞、收藏或评论区聊聊你的踩坑经历。
