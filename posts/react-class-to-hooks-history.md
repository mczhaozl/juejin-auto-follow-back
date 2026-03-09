# React 从 Class 到 Hooks：为什么「放弃」类组件走向函数式

> 按时间线讲清 React 从 Class 到 Hooks 的演变、复用痛点与 this/生命周期问题，以及为何官方推荐函数组件 + Hooks。

---

## Class 时期：React 的起点（2013-2018）

### 历史背景

2013 年 5 月，Facebook 工程师 **Jordan Walke** 在 JSConf US 上首次公开介绍了 **React**。React 并非凭空出现——它源自 Walke 早年在公司内部做的 **FaxJS** 项目，用来弥补当时 Facebook 内部 MVC 框架 **BoltJS** 的不足。FaxJS 里已经埋下了我们今天熟悉的概念：**组件化、props、state、声明式 UI 与高效的 diff 更新**。开源后的 React 很快以「组件 + 单向数据流 + 虚拟 DOM」的形象被前端圈接受，而那时**组件几乎清一色是 Class**：你要用 state 和生命周期，就得写 `React.Component` 子类。

那个年代的典型写法是这样的：

```javascript
// React 0.14 / 15 / 16 早期：有状态组件的标准写法
class Counter extends React.Component {
    constructor(props) {
        super(props);
        this.state = { count: 0 };
        this.handleClick = this.handleClick.bind(this);  // 必须手动 bind this
    }

    handleClick() {
        this.setState({ count: this.state.count + 1 });
    }

    componentDidMount() {
        document.title = `点击了 ${this.state.count} 次`;
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevState.count !== this.state.count) {
            document.title = `点击了 ${this.state.count} 次`;
        }
    }

    render() {
        return (
            <button onClick={this.handleClick}>
                点击次数：{this.state.count}
            </button>
        );
    }
}
```

**为什么一开始就用 Class？** 因为 ES6 之前没有标准化的「类」语法，React 提供了 `React.createClass`；ES6 普及后，React 推荐用 `extends React.Component`，以便使用 `this.state`、`this.setState` 和 `componentDidMount`、`componentDidUpdate` 等生命周期。那时**函数组件只能做「无状态展示」**，一旦要状态或副作用，就必须上 Class。于是整个生态——文档、教程、开源库——都围绕 Class 组件来写，Class 成了 React 的默认面孔。

### 标志性事件

- **2013 年 5 月**：React 在 JSConf US 首次公开，由 Jordan Walke 介绍；开源库旨在简化 UI 与组件开发。
- **2015 年**：React 0.14 起支持**函数组件**（无 state、无生命周期），但复杂交互仍依赖 Class；同年 ES6 普及，`class` 语法成为官方推荐。
- **2016–2017 年**：**高阶组件（HOC）** 与 **render props** 成为「逻辑复用」的主流方案，Class 组件被层层包装，嵌套越来越深。
- **2018 年前**：React 官方文档与社区最佳实践都以 Class 为主；函数组件仅用于简单展示，状态逻辑复用没有统一、优雅的方式。

### 解决的问题与遗留问题

Class 组件让 React 在当年能够清晰表达「有状态 + 生命周期」：`constructor` 里初始化 state、`componentDidMount` 里拉数据、`componentDidUpdate` 里根据 props/state 同步副作用、`render` 里描述 UI。但很快暴露出几类问题：**逻辑复用**要靠 HOC 或 render props，容易变成「包装地狱」；**this 绑定**必须记得 `bind` 或箭头函数，否则事件回调里 `this` 丢光；**同一块逻辑**被生命周期拆成 `componentDidMount` 和 `componentDidUpdate` 两处，难以按「功能」组织代码。这些痛点为后来 Hooks 的诞生埋下伏笔。

---

## 痛点时期：复用、this 与「包装地狱」（2015-2018）

### 历史背景

随着业务复杂度上升，大家迫切需要**在多个组件之间复用「带 state 的逻辑」**：比如「订阅窗口尺寸」「监听键盘」「请求用户信息并缓存」。Class 组件本身没有「抽出一块可复用逻辑」的官方方式，于是社区摸索出两种主流模式：**高阶组件（HOC）** 和 **render props**。做法都是「外面包一层，把逻辑通过 props 注入进去」。组件一多，就会变成一层套一层：`withAuth(withTheme(withRouter(MyComponent)))`，DevTools 里一展开全是 `WithAuth(WithTheme(WithRouter(...)))`，可读性和调试成本都很高——这就是 React 官方后来点名的 **wrapper hell（包装地狱）**。

同时，Class 里 **this** 的绑定问题一直让人头疼：不 `bind` 的话，`onClick={this.handleClick}` 在回调执行时 `this` 是 `undefined`；在 `constructor` 里写 `this.handleClick = this.handleClick.bind(this)` 又啰嗦；用箭头函数 `handleClick = () => {}` 可以避免 bind，但语法和「类字段」的兼容性在早期并不统一。再就是**生命周期把「同一件事」拆成多块**：比如「根据 count 同步 document.title」，在 Class 里要写在 `componentDidMount` 和 `componentDidUpdate` 两处，逻辑重复，还容易漏掉依赖。

### 标志性事件

- **2015 年后**：HOC 模式在 React 生态中大量使用，React 官方文档推荐用 HOC 做「横切」逻辑；Redux 的 `connect`、React Router 的 `withRouter` 都是典型 HOC。
- **2016–2017 年**：**render props** 流行（如 `<Mouse render={({ x, y }) => <div>{x},{y}</div>}`），逻辑复用多了一种写法，但嵌套与可读性仍不理想。
- **2018 年前**：React 团队在内部与社区反馈中反复遇到「复用难、this 烦、生命周期割裂逻辑」的抱怨，开始探索不依赖 Class 的解决方案。

### 典型痛点代码示例

**1. 逻辑复用：HOC 嵌套成「包装地狱」**

```javascript
// 多个 HOC 叠加：withUser, withWindowSize, withTheme...
function withUser(WrappedComponent) {
    return class extends React.Component {
        state = { user: null };
        componentDidMount() {
            fetchUser().then(user => this.setState({ user }));
        }
        render() {
            return <WrappedComponent user={this.state.user} {...this.props} />;
        }
    };
}
function withWindowSize(WrappedComponent) {
    return class extends React.Component {
        state = { width: window.innerWidth, height: window.innerHeight };
        componentDidMount() {
            const handler = () => this.setState({ width: window.innerWidth, height: window.innerHeight });
            window.addEventListener('resize', handler);
            this.remove = () => window.removeEventListener('resize', handler);
        }
        componentWillUnmount() { this.remove?.(); }
        render() {
            return <WrappedComponent windowSize={this.state} {...this.props} />;
        }
    };
}
// 使用：嵌套多、DevTools 里组件名一长串
const MyPage = withUser(withWindowSize(function MyPage({ user, windowSize }) {
    return <div>{user?.name} — {windowSize.width}px</div>;
}));
```

**2. 同一逻辑被生命周期拆成两处**

```javascript
// 同步 document.title：mount 要写一遍，update 又要写一遍，依赖一多就容易漏
class Page extends React.Component {
    componentDidMount() {
        document.title = `${this.props.title} - 我的应用`;
    }
    componentDidUpdate(prevProps) {
        if (prevProps.title !== this.props.title) {
            document.title = `${this.props.title} - 我的应用`;
        }
    }
    // ...
}
```

**3. this 绑定：必须记得 bind 或类字段**

```javascript
class Form extends React.Component {
    handleSubmit() {
        console.log(this);  // 若不做 bind，这里是 undefined
        this.setState({ submitted: true });
    }
    render() {
        return <form onSubmit={this.handleSubmit.bind(this)}>...</form>;
        // 或 constructor 里：this.handleSubmit = this.handleSubmit.bind(this);
    }
}
```

这些痛点共同推动 React 团队去寻找一种**不依赖 Class、能按「逻辑块」组织、且易于复用**的新方案——也就是后来的 Hooks。

---

## Hooks 诞生：从提案到稳定（2018-2019）

### 历史背景

2018 年 10 月 25–26 日，**React Conf 2018** 在美国 Henderson 举行。第一天的主 Keynote「**React Today and Tomorrow**」由 **Sophie Alpert** 和 **Dan Abramov** 主讲，正式向外界介绍了 **Hooks**：一种在**函数组件**里使用 state 和副作用的提案，无需 Class，无需 `this`，且能把「一块逻辑」收拢成可复用的 **自定义 Hook**。当时 Hooks 被放在 **React 16.7 alpha** 里供尝鲜；官方博客明确说：Hooks 让我们可以**用函数组件做到 Class 能做的一切**，并且更好地复用状态逻辑、避免 wrapper hell。

随后版本号经历了一次「乌龙」：2018 年 12 月发布的 **React 16.7 正式版** 并没有包含 Hooks。团队在博客中解释：之前把「未发布特性」和具体版本号绑在一起是个失误，Hooks 会在「几个月内」推出。果然，**2019 年 2 月 6 日**，**React 16.8** 正式发布，Hooks 成为稳定特性，并在 React DOM、React DOM Server、Shallow Renderer、Test Renderer 中全面支持；React Native 0.59 也跟进支持。从那以后，**函数组件 + Hooks** 成为 React 官方推荐的默认写法。

### 标志性事件

- **2018 年 10 月 25–26 日**：React Conf 2018，Sophie Alpert 与 Dan Abramov 在 Keynote「React Today and Tomorrow」中首次公开介绍 Hooks；React 16.7 alpha 提供 Hooks 尝鲜。
- **2018 年 12 月**：React 16.7 正式版发布，**未**包含 Hooks；官方澄清版本号与未发布特性的关系，承诺数月内推出。
- **2019 年 2 月 6 日**：**React 16.8** 发布，Hooks 稳定可用；所有相关包需升级到 16.8.0+，Hooks 成为推荐用法。

### 同一需求用 Hooks 重写

前面「计数器 + 同步 document.title」和「窗口尺寸 + 用户信息」的逻辑，用 Hooks 可以写成下面这样，逻辑按「功能」聚在一起，且易于复用：

```javascript
// 计数器 + 同步 title：一块逻辑一个 useEffect，无需拆成 mount/update
function Counter() {
    const [count, setCount] = useState(0);
    useEffect(() => {
        document.title = `点击了 ${count} 次`;
    }, [count]);
    return <button onClick={() => setCount(c => c + 1)}>点击次数：{count}</button>;
}

// 逻辑复用：自定义 Hook，无 HOC、无 render props、无嵌套
function useWindowSize() {
    const [size, setSize] = useState({ width: window.innerWidth, height: window.innerHeight });
    useEffect(() => {
        const handler = () => setSize({ width: window.innerWidth, height: window.innerHeight });
        window.addEventListener('resize', handler);
        return () => window.removeEventListener('resize', handler);
    }, []);
    return size;
}
function useUser() {
    const [user, setUser] = useState(null);
    useEffect(() => {
        fetchUser().then(setUser);
    }, []);
    return user;
}
// 使用：直接调用，无包装
function MyPage() {
    const user = useUser();
    const windowSize = useWindowSize();
    return <div>{user?.name} — {windowSize.width}px</div>;
}
```

**Hooks 带来的变化**：状态用 `useState`，副作用用 `useEffect`，依赖写在数组里，React 负责在依赖变化时重新执行；**没有 this**，没有 bind；**复用**靠自定义 Hook（以 `use` 开头的函数），不再需要 HOC 或 render props 的层层包装。这就是「React 放弃 Class、走向 Hooks」的直观体现：不是从语法上删除 Class，而是**官方推荐与生态全面转向「函数组件 + Hooks」**。

---

## 为什么 React「放弃」Class、走向 Hooks？

React 并没有在运行时禁止 Class 组件，至今 Class 仍可正常使用。所谓「放弃」指的是：**官方文档、新示例和最佳实践都以函数组件 + Hooks 为首选**，新特性（如 Concurrent 模式、Suspense 等）的设计也围绕「组件即函数」的模型展开。原因可以概括为下面几条。

### 1. 逻辑复用：从「包装」到「抽取」

Class 时代复用带 state 的逻辑只能靠 **HOC** 或 **render props**，结果就是 wrapper hell——组件树又深又难读。Hooks 用 **自定义 Hook** 把「一块状态 + 一段副作用」抽成 `useXxx()`，在组件里直接调用即可，无需改组件层级、无需额外包装，这是 React 官方在 [Introducing Hooks](https://reactjs.org/docs/hooks-intro.html) 里强调的核心动机之一。

### 2. 代码组织：按「功能」而非「生命周期」

Class 里「根据 A 同步 B」这类逻辑往往要拆到 `componentDidMount` 和 `componentDidUpdate` 两处，相关代码分散。Hooks 里一个 `useEffect` 对应「这一块副作用 + 其依赖」，相关逻辑写在一起，更符合「按功能组织」的阅读习惯，也减少遗漏依赖或重复代码。

### 3. 去掉 this，降低心智负担

Class 组件里 `this` 的指向、`bind`、箭头函数类字段是新手和面试的高频坑。函数组件 + Hooks 没有 `this`，所有 state 和更新函数都来自 `useState` 等 API，闭包清晰，调试和复用都更简单。

### 4. 与未来特性对齐

Concurrent 模式、Suspense、以及 React 18 的并发渲染等，在设计上更贴合「组件即纯函数 + 显式依赖」的模型。Hooks 的依赖数组和「每次渲染独立快照」的语义，便于 React 在后台做中断与恢复，而 Class 的生命周期模型与这类能力更难无缝对接。因此**新能力优先甚至只面向函数组件**，客观上加速了「从 Class 到 Hooks」的迁移。

---

## 总结：一条时间线串起来

- **2013–2018（Class 时期）**：React 诞生于 2013 年 JSConf US，组件以 Class 为主；state、生命周期、this 绑定和 HOC/render props 复用成为标配，同时带来包装地狱、this 问题和生命周期割裂逻辑的痛点。
- **2015–2018（痛点凸显）**：HOC 与 render props 大量使用，逻辑复用与代码组织问题被反复提及；React 团队在社区反馈与内部实践中开始探索不依赖 Class 的方案。
- **2018–2019（Hooks 落地）**：React Conf 2018 首次公开 Hooks；2019 年 2 月 React 16.8 稳定发布，函数组件 + Hooks 成为官方推荐；逻辑复用、代码组织、无 this、与未来特性对齐，共同构成「放弃 Class、走向 Hooks」的原因。

**一句话**：React 没有从语法上消灭 Class，但通过 Hooks 把「有状态 + 副作用」完整移到了函数组件上，用更清晰的复用方式和更少的样板代码，把 Class 挤到了「兼容旧项目」的位置；新代码默认用函数 + Hooks，就是「为什么 React 放弃了 Class、走向 Hooks」的答案。

**延伸阅读**：[React 官方 - Introducing Hooks](https://reactjs.org/docs/hooks-intro.html)、[React v16.8: The One With Hooks](https://reactjs.org/blog/2019/02/06/react-v16-8-0.html)、[Hooks FAQ](https://legacy.reactjs.org/docs/hooks-faq.html)。若对你有用，欢迎点赞、收藏或评论区聊聊你在 Class 转 Hooks 时踩过的坑。
