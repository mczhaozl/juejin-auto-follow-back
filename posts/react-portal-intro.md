# React Portal 介绍：项目迭代里「弹窗被裁、层级错乱」怎么破

> 以弹窗被裁、z-index 打架为切入，并补充「外层随路由变、内部不好改」时用 Portal 渲染外层的用法与注意点。

---

## 一、项目迭代中遇到的典型问题

我们在做后台管理系统或中台页面的迭代时，经常遇到这两类现象：

### 1. 弹窗 / 抽屉被「裁掉」一截

**场景**：页面里有一块可滚动区域，用了 `overflow: hidden` 或 `overflow: auto`（例如表格外层、侧边栏、带圆角的卡片）。在这一块内部打开的 **Modal / Drawer / 下拉菜单**，会有一半露在容器外、一半被裁掉，或者滚动时跟着容器一起滚，而不是盖在全屏之上。

**原因**：组件的 DOM 节点写在「有 overflow 的祖先」下面。浏览器会按照 **包含块（containing block）** 和 **层叠上下文（stacking context）** 来裁剪和绘制，子节点再大的 `z-index` 也逃不出父级的裁剪区域。

### 2. z-index 打架，谁盖住谁说不清

**场景**：头部导航的 dropdown 要盖住下面的内容，结果被下面某块「带 transform / opacity / filter 的 div」盖住；或者多个 Modal 叠在一起，期望「后打开的盖住先打开的」，结果顺序反了。

**原因**：一旦父级创建了新的层叠上下文，子元素的 `z-index` 只在这个上下文内部比较，无法和「兄弟分支」比高低。组件树写在哪、DOM 就长在哪，光调 z-index 很难理顺全局层级。

### 小结：问题本质

**弹窗、浮层、全局提示** 这类 UI，从交互上应该是「盖住整页」或「相对视口定位」，但若它们的 DOM 仍然挂在「带 overflow 或层叠上下文的父节点」下面，就会受限于父级的裁剪和层级。要解决，要么把这类节点的 **DOM 挂到更外层**（如 `document.body`），要么用 CSS 大改结构——React 提供的 **Portal** 就是在「不破坏组件树」的前提下，把子节点渲染到指定 DOM 容器里，正好对应「项目迭代中遇到的这些问题」。

---

## 二、Portal 是什么、解决了什么问题

**Portal** 是 React DOM 提供的机制：**把一段 React 子节点渲染到「父组件所在 DOM 树之外」的另一个 DOM 节点里**。  
API 是 `createPortal`，来自 `react-dom`：

```javascript
import { createPortal } from 'react-dom';

createPortal(child, container);
createPortal(child, container, key?);
```

- **child**：任意可渲染的 React 内容（JSX、字符串、数字等）。
- **container**：已经存在的 DOM 节点，例如 `document.body` 或 `document.getElementById('modal-root')`。
- **key**（可选）：给 Portal 一个稳定标识，便于 React 协调。

**解决了什么问题？**

1. ** overflow 裁剪**：把 Modal/抽屉/Dropdown 的 DOM 挂到 `document.body`（或页面根级容器），就不再受业务布局里 `overflow: hidden` 影响，不会被裁掉。
2. **层级可控**：浮层统一挂到同一层级，用 `z-index` 或 CSS 变量统一管理「谁在上谁在下」，避免和业务 DOM 的层叠上下文混在一起。
3. **结构清晰**：组件在代码里仍然写在「使用它的父组件」下面，逻辑关系不变；只是最终 DOM 长在别处，**不破坏组件树、不破坏 Context 和事件冒泡**。

---

## 三、在项目里怎么用：一个 Modal 示例

下面是一个「用 Portal 把内容挂到 body」的简单 Modal，可直接套进现有项目。

### 1. 准备一个挂载点（可选但推荐）

在 `index.html` 里留一个专门给「全局浮层」用的节点，方便以后做统一样式或清理：

```html
<!-- public/index.html -->
<div id="root"></div>
<div id="modal-root"></div>
```

### 2. 用 createPortal 把内容渲染过去

```javascript
import { createPortal } from 'react-dom';

function Modal({ open, onClose, children }) {
    if (!open) return null;

    const container = document.getElementById('modal-root') || document.body;

    return createPortal(
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                {children}
            </div>
        </div>,
        container
    );
}

// 使用：写在任意深层组件里，DOM 会挂到 modal-root
function Page() {
    const [open, setOpen] = useState(false);
    return (
        <div style={{ overflow: 'hidden', height: 200 }}>
            <button onClick={() => setOpen(true)}>打开弹窗</button>
            <Modal open={open} onClose={() => setOpen(false)}>
                <p>即使父级有 overflow:hidden，我也能完整显示</p>
            </Modal>
        </div>
    );
}
```

**效果**：`Modal` 在组件树里仍是 `Page` 的子组件，但实际 DOM 被渲染到 `#modal-root`，不再被父级的 `overflow: hidden` 裁剪；**事件冒泡** 仍按 React 树走，所以 `onClose`、Context 都正常。

### 3. 样式要点（避免再被裁）

-  overlay 建议**全屏定位**（如 `position: fixed; inset: 0`），并设一个较高的 `z-index`（或通过 CSS 变量统一管理）。
- 若使用 `border-radius`，给 overlay 或 content 设 **overflow: hidden** 时，注意只作用在浮层自身，不影响页面其他区域。

---

## 四、另一类场景：外层要随路由变，但内部不好改

路由嵌套好几层之后，经常还有一类需求：**外面的布局（例如顶部 Tab、面包屑、操作栏）也要跟着当前路由变**。理想情况是「当前是哪个路由，外层就渲染哪套 UI」，但若**内部路由结构不好动**（历史包袱、多人协作、改造成本高），Portal 就能派上用场。

### 做法一：外层根据路由判断来渲染

一种做法是**在外层 Layout 里根据路由做条件渲染**：用 `useLocation()` 或路由配置判断当前 path，再决定渲染哪一块头部/面包屑。这样「外层跟着路由变」的逻辑集中在外层，清晰可控。

```javascript
// 外层 Layout：根据路由决定渲染什么
function AppLayout() {
    const location = useLocation();
    const isDetail = location.pathname.includes('/detail');
    return (
        <>
            <header>
                {isDetail ? <DetailHeader /> : <DefaultHeader />}
            </header>
            <main>
                <Outlet />  {/* 内层路由出口 */}
            </main>
        </>
    );
}
```

前提是**能改外层**：Layout 里要能拿到路由、能加分支。若 Layout 是公共的、不好动，或者「该渲染什么」的逻辑其实写在各个子路由里更合适，就会遇到「内部不好改」的情况。

### 做法二：内部不好改时，Portal 把「外层 UI」挂到外层 DOM

**内部不好改** 指的是：不想大动路由结构、不想把一堆「当前页该显示什么头部」的逻辑都提到最外层，或者外层 Layout 是通用组件、不方便塞满路由分支。这时可以：

- 在 **HTML 里给「外层占位」留一个挂载点**，例如 `<div id="layout-header-slot"></div>`，放在 Layout 的 header 区域。
- 在**各个子路由组件内部**（哪怕嵌套很深），根据当前路由用 **Portal** 把「这一页该显示的头部/面包屑」渲染到 `#layout-header-slot`。

这样**外层 DOM 结构不变**，始终有一个 slot；**谁往 slot 里渲染、渲染什么**，由当前匹配到的路由组件决定，内部不用大改路由层级，只是多了一个「往 slot 里 Portal 一下」的职责。

```javascript
// 子路由组件（可能嵌套在好几层之下）
function DetailPage() {
    const container = document.getElementById('layout-header-slot');
    return (
        <>
            {container && createPortal(
                <DetailBreadcrumb />,
                container
            )}
            <div className="detail-content">...</div>
        </>
    );
}
```

**效果**：用户看到的「外层」头部/面包屑会随路由变，但实现上是由**当前页组件**通过 Portal 把内容「投递」到外层挂载点；外层 Layout 不用写一堆 `if (path === ...)`，内部路由也不用大改，只是各自负责「往 slot 里填什么」。这就是「路由写了好几层、外面也要跟着路由变，但内部不好改」时，**Portal 派上用场**的典型用法。

---

## 五、需要注意的两点

### 1. 事件冒泡按 React 树，不按 DOM 树

Portal 只改变 **DOM 位置**，不改变 **React 组件树**。因此，Portal 内部触发的点击等事件，会**冒泡到 React 树上的父组件**，而不是 DOM 上的父节点。这样你在 `<Page>` 里写 `<Modal>`，Modal 里的按钮事件仍然可以被 Page 或更上层的 React 组件接收，便于做统一关闭逻辑或 Context 消费。

### 2. Context 照常可用

Portal 里的子组件**仍然能访问「React 树」上父节点提供的 Context**，因为 React 认的是组件层级，不是 DOM 层级。所以把 Theme、Router、状态等 Context 用在 Modal 里没问题。

---

## 六、总结

- **项目迭代中** 常遇到：弹窗/抽屉被父级 **overflow 裁剪**、**z-index 层级** 理不清；以及**路由嵌套多、外层布局要随路由变，但内部不好改**。
- **React Portal**（`createPortal`）把子节点渲染到指定 DOM 容器，只改 DOM 位置，不改组件树。既可把 Modal 挂到 `body` 解决裁剪/层级，也可把「外层该显示的头部/面包屑」从深层路由组件里 Portal 到外层 slot，让外层跟着路由变而无需大动内部结构。
- **用法**：`createPortal(children, container)`，container 可以是 `#modal-root`、`#layout-header-slot` 等；浮层或「投递到外层的 UI」仍写在业务组件里，逻辑清晰。
- **注意**：事件冒泡、Context 都按 React 树走；样式上浮层用全屏 + 合适 z-index；挂载点需已存在（如 `document.getElementById(...)` 再做 Portal）。

若对你有用，欢迎点赞、收藏；你们项目里若有用 Portal 做 Modal 或「外层随路由变」的实践，也欢迎在评论区分享。
