# JS Event Loop 前世今生：从同步世界到调度大师（完整演变史）

> 按时间线拆解 Event Loop 的每一个阶段：每段都有明确年份与标志性事件，配历史背景和代码示例，带你从 1995 年走到今天，把「单线程 + 任务队列 + 微任务」的来龙去脉一次搞清。

---

## 远古时期：同步的世界（1995-2009）

### 历史背景

1995 年，Brendan Eich 在 Netscape 公司用大约 10 天时间创造了 JavaScript（最初叫 LiveScript，后因与 Sun 合作改名为 JavaScript）。当时的设计目标非常简单：**为浏览器提供简单的页面交互能力**，比如表单验证、按钮点击响应、简单的 DOM 操作。那会儿没有「异步」这个概念——脚本就是从上到下执行完就结束，顶多响应一下用户点击或表单提交。

那个年代的网页长这样：

```html
<!-- 1995–2000 年代的典型写法 -->
<form onsubmit="return validateForm()">
  <input type="text" name="username" />
  <button type="submit">提交</button>
</form>

<script>
function validateForm() {
  var username = document.forms[0].username.value;
  if (username === '') {
    alert('用户名不能为空！');
    return false;
  }
  return true;
}
</script>
```

这个时期的 JavaScript 只需要处理简单的同步操作：

```javascript
// 计算：同步执行到底
var result = 1 + 2;

// DOM 操作：事件绑定也是「同步注册」，回调在用户点击后才执行
document.getElementById('btn').onclick = function() {
  alert('你点击了按钮');
};

// 表单验证：同步判断
function validate(value) {
  return value.length > 0;
}
```

### 标志性事件

- **1995 年**：Brendan Eich 在 Netscape 创造 JavaScript（LiveScript → JavaScript）；同年 Netscape Navigator 2 搭载 JS 引擎。
- **1996 年**：微软在 IE3 中推出 JScript，与 Netscape 竞争，语法兼容但实现各异；各厂对「何时执行定时器、事件」没有统一规范。
- **1997 年**：ECMAScript 1（ES1）发布，JS 有了语言标准，但**标准里没有定义「事件循环」或「任务队列」**，只规定了语法和执行语义；调度完全由宿主（浏览器）自行实现。
- **2000 年代初期**：各浏览器陆续实现 `setTimeout` / `setInterval`，但最小延迟、嵌套定时器的节流方式等行为细节不统一，尚未形成统一的「Event Loop」规范。

### 为什么只有同步？

因为当时的网页交互非常简单：没有「不刷新页面就发请求」的需求，即使要跟服务器通信，也是通过**表单提交、整页刷新**完成的。脚本只需要在页面加载时跑一遍，或响应用户的一次点击、一次提交，不需要「等网络回来再执行下一段逻辑」。所以引擎的设计就是：**一条调用栈，执行完就结束**；事件（如点击）由浏览器在底层记录，用户触发时再调你注册的回调，但那时还没有一个被规范写死的「事件循环」名字。换句话说，**「先执行完当前脚本，再响应下一个用户动作」** 这种顺序，已经隐含了「排队」的思维，只是还没有被抽象成统一的任务队列与 Loop 概念。

**当时的引擎大致怎么工作？** 加载页面时执行顶层脚本，遇到 `onclick`、`onsubmit` 就只做「注册」——把函数引用存起来；用户点击或提交时，由浏览器底层把对应的回调推给引擎执行。没有定时器时，不存在「延后执行」的队列；有了 setTimeout 之后，才需要「到点再执行」的队列，这就是任务队列的前身。

---

## 转折点：定时器与事件（1997-2005）

### 历史背景

随着 `setTimeout` 和 `setInterval` 的普及，以及 DOM 事件（click、load、keydown 等）的标准化，浏览器面临一个新问题：**当前脚本正在执行时，定时器到点了、用户点了按钮，这些「延后要执行」的回调该放在哪里？** 于是各厂商在实现里不约而同地引入了「任务队列」的雏形：把到点的定时器、触发的 DOM 事件放进一个队列，等当前脚本执行完后，再从队列里取一个任务执行，执行完再取下一个——这就是最原始的 **Loop**：取任务 → 执行 → 再取 → 再执行。此时还没有「微任务」，所有异步回调一视同仁，先到先得。

### 标志性事件

- **1997 年前后**：Netscape 与 IE 相继实现 `setTimeout` / `setInterval`，JS 首次有了「延后执行」的标准 API。
- **2000 年**：DOM Level 2 事件模型普及，`addEventListener`、事件冒泡/捕获成为标准，浏览器需要统一调度「何时执行用户注册的回调」。
- **2004 年**：WHATWG 成立，开始推动 HTML 与相关 Web API 的标准化，为后来「Event Loop」写进规范埋下伏笔。
- **2005 年**：Gmail、Google Maps 等产品大规模使用 **AJAX**（Asynchronous JavaScript and XML），网页可以在不刷新的情况下与服务器通信，「异步」正式成为前端核心需求。

### 解决的问题

定时器和事件回调让 JavaScript 能够**在不阻塞主线程**的前提下「等」用户操作或时间点：

```javascript
// 定时器：到点再执行
setTimeout(function() {
  console.log('3 秒后执行');
}, 3000);

// 事件：用户点击后再执行
document.getElementById('btn').onclick = function() {
  alert('你点击了按钮');
};

// 此时还没有 Promise，异步只能靠回调和定时器
```

此时引擎的模型已经变成：**单线程 + 任务队列**。但「Event Loop」这个词还没被写进任何一份正式规范，各浏览器实现细节也不完全一致。**当时开发者如何理解执行顺序？** 只能靠经验：定时器回调一定在当前脚本之后；多个 setTimeout(0) 一般按注册顺序执行；事件回调在用户操作后、由浏览器在「合适的时机」塞进队列——这个「合适的时机」后来被规范写死，就是「取一个 task → 执行完 → 再取下一个」。

---

## Callback 时期：回调地狱的噩梦（2005-2015）

### 历史背景

AJAX 流行之后，前端逻辑变复杂：先请求 A，拿到结果再请求 B，再根据 B 的结果做 DOM 更新或再请求 C……一层层嵌套的回调就成了「回调地狱」。同时，**Node.js 在 2009 年诞生**，JavaScript 进入服务端，异步 I/O 成为核心：读文件、查数据库、发 HTTP 请求，全部依赖回调。Event Loop 在浏览器和 Node 里都成了「事实上的运行模型」，但规范仍然滞后，开发者只能靠经验和文档理解「执行顺序」。

### 标志性事件

- **2005 年**：AJAX 技术被广泛应用，Gmail、Google Maps 展示无刷新交互；回调函数成为处理异步结果的主流方式。
- **2009 年**：Node.js 诞生（Ryan Dahl），JavaScript 进入服务端；**libuv** 作为跨平台异步 I/O 库被引入，Node 拥有了一套与浏览器不同的 Event Loop 实现（多阶段）。
- **2009 年**：HTML5 草案中开始出现与「事件循环」相关的描述，WHATWG 与 W3C 推进相关规范。
- **2010 年前后**：回调函数成为异步编程的绝对主流，jQuery 的 `$.ajax(success: fn)`、Node 的 `fs.readFile(path, callback)` 遍地开花；「回调地狱」成为高频吐槽。

### 解决的问题与带来的新问题

回调让 JS 能够处理异步 I/O 而不阻塞主线程，但嵌套一深就难以维护：

```javascript
// 典型的「回调地狱」：先请求 A，再请求 B，再更新 DOM
getUser(id, function(user) {
  getOrders(user.id, function(orders) {
    getDetail(orders[0].id, function(detail) {
      document.getElementById('result').innerText = detail.name;
    });
  });
});
```

**用 XMLHttpRequest 的典型写法**（那时还没有 fetch）：

```javascript
var xhr = new XMLHttpRequest();
xhr.open('GET', '/api/user');
xhr.onreadystatechange = function() {
  if (xhr.readyState === 4) {
    var data = JSON.parse(xhr.responseText);
    getOrders(data.id, function(orders) {
      // 又是一层回调……
    });
  }
};
xhr.send();
```

**jQuery 与 Node 的 callback 风格**：前端用 `$.ajax({ success: fn })`、`$.get(url, fn)`，Node 用 `fs.readFile(path, (err, data) => {})`、`http.get(url, callback)`；都是「把结果交给回调」，执行时机都由 Event Loop 调度——I/O 完成后，由底层把回调推进任务队列，主线程取到就执行。差别只在前端多了一个「渲染」步骤，Node 多了多阶段与 nextTick。

此时**任务队列**已经稳定存在：setTimeout、I/O 完成、DOM 事件都会往队列里塞回调；但还没有「微任务」概念，所以所有回调按入队顺序执行，无法实现「高优先级插队」。这也为后来 Promise 与微任务的引入埋下伏笔：**大家迫切需要一种「在当前任务屁股后面立刻执行」的机制**，而不是和所有 setTimeout、I/O 混在一个队列里排队。

---

## 规范落地：HTML5 与 Event Loop 命名（2009-2015）

### 历史背景

WHATWG 与 W3C 在推进 HTML5 时，把「脚本如何被调度执行」写进了标准。这就是我们今天说的 **Event Loop** 的正式出处：**它不是 ECMAScript 的一部分，而是 HTML 标准（Living Standard）里对「浏览器环境中 JS 执行模型」的约定**。规范里明确了「任务」（task，后来常被叫成 macrotask）的来源：一段 script、setTimeout/setInterval、I/O、UI 事件等；并且为后来的「微任务」留出了位置——先有概念，再在 Promise 普及后把微任务队列写细。

### 标志性事件

- **2009–2011 年**：HTML5 草案中逐步出现事件循环、任务队列的描述；WHATWG 的 Living Standard 成为事实上的参考。
- **2011 年**：ES5.1 发布，仍无 Promise，异步仍以回调和定时器为主。
- **2012 年**：Promises/A+ 社区规范出现，为 ES6 Promise 铺路；规范开始讨论「then 回调应该在当前任务结束后、下一个任务前执行」，即后来的微任务语义。
- **2014 年**：HTML5 中 Event Loop 的规范描述趋于稳定，任务与微任务（microtask）的区分被明确写入 [HTML Standard](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)。WHATWG 与 W3C 在 HTML 上的分工也逐渐清晰：Living Standard 由 WHATWG 维护，W3C 做快照与互操作；Event Loop 的权威描述在 WHATWG 的 HTML 标准中。

### 规范说了什么

- 存在**多个任务队列**（如定时器、I/O、事件各有一类），但执行时**每轮只取一个 task** 执行到底。
- 执行完一个 task 后，在取下一个 task 之前，必须**清空当前的所有 microtask**（微任务）。
- 微任务的来源后来被定义为：Promise 的 then/catch/finally、`queueMicrotask()`、MutationObserver 等。

**规范里具体写了啥？** 在 HTML Living Standard 里，Event Loop 的算法大致是：每个 event loop 有一个或多个 task queues；每轮从某个 task queue 里取一个 **task** 执行（run a task）；该 task 执行完后，执行 **microtask checkpoint**，即清空当前所有 microtask；然后若需要 **update the rendering**，再做渲染；最后再取下一个 task。所以「取一个 task → 清空 microtask → 渲染（如需）→ 再取 task」是写死在规范里的。ECMAScript 从未定义 Event Loop，它只定义「怎么执行代码」；「什么时候执行哪段代码」由宿主环境（HTML 标准、Node）决定，所以看执行顺序和调度，一定要去查 HTML 或 Node 的文档，而不是 ES 规范。

---

## Promise 与微任务时代（2015 至今）

### 历史背景

ES6（ECMAScript 2015）正式引入 **Promise**，前端和 Node 都开始大量使用 then 链式调用替代回调。规范规定：Promise 的 then/catch/finally 回调必须作为 **microtask** 入队，从而在「当前宏任务结束后、下一个宏任务前」执行。这样既避免了回调地狱，又让高优先级异步（如 DOM 更新后的逻辑）能够「插队」到下一个 setTimeout 甚至下一次渲染之前。随后，`queueMicrotask()`、MutationObserver 等也被明确为微任务来源，Event Loop 的「双队列」（宏任务 + 微任务）模型彻底定型。

### 标志性事件

- **2015 年**：ES6 发布，Promise 成为语言标准；各引擎实现 then 回调为微任务，与 HTML 标准中的 Event Loop 描述对齐。
- **2015 年后**：前端框架（Vue、React）与 Node 生态全面拥抱 Promise；async/await（ES2017）基于 Promise，进一步巩固「微任务」在开发者心智中的地位。
- **2018 年**：`queueMicrotask()` 在部分环境中可用，后被纳入标准，用于「在当前任务结束后、下一个任务前」执行回调。
- **至今**：HTML Living Standard 与 ECMAScript 协同演进，Event Loop（浏览器）与 Node 的 libuv 多阶段 Loop 成为面试与调优的必考内容。

### 解决的问题与经典题

微任务让 then 回调总能抢在「下一个 setTimeout」之前执行：

```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
console.log('4');
// 输出：1 4 3 2
```

顺序是：当前 script（宏任务）打 1、4 → 清空微任务打 3 → 下一个宏任务（setTimeout）打 2。面试官问「setTimeout(fn, 0) 和 Promise.then(fn) 谁先」——答案就是：**then 先**，因为 then 是微任务，会在当前宏任务结束后立刻被清空，而 setTimeout 是下一个宏任务。

**浏览器里一轮 Loop 的四步口诀**（建议背下来）：

1. 取一个**宏任务**（如一段 script、或一个 setTimeout 回调）执行到底；
2. **栈空后**，把当前**微任务队列**里能跑的全跑完（then、queueMicrotask、MutationObserver）；
3. 若需要**渲染**，在此刻做（约 60fps）；
4. 回到步骤 1，取下一个宏任务。

再练一题，巩固「微任务同层、按入队顺序执行」：

```javascript
console.log('A');
setTimeout(() => console.log('B'), 0);
queueMicrotask(() => console.log('C'));
Promise.resolve().then(() => console.log('D')).then(() => console.log('E'));
console.log('F');
// 输出：A F C D E B
```

**综合面试题：一段代码走完整个 Loop**（在浏览器控制台跑）：

```javascript
async function go() {
  console.log('1');
  await Promise.resolve();
  console.log('2');
}
console.log('3');
setTimeout(() => console.log('4'), 0);
go();
Promise.resolve().then(() => console.log('5'));
console.log('6');
// 输出：3 1 6 2 5 4
```

解释：3、1、6 是同步（go 里 await 前也是同步）；然后清微任务：await 后的 2、then 的 5；最后宏任务 setTimeout 的 4。这样就把「同步 → 微任务 → 下一宏任务」串起来了。

**微任务里再 then 会怎样？** 当前宏任务结束后，引擎会**一直**清微任务队列直到空。所以你在 then 里再 then、再 queueMicrotask，这些新入队的微任务都会在本轮被依次执行完，然后才取下一个宏任务。例如：

```javascript
Promise.resolve().then(() => {
  console.log('a');
  Promise.resolve().then(() => console.log('b'));
}).then(() => console.log('c'));
// 输出：a b c（第一层 then 打 a 并入队 b，本 then 完成后第二层 then 入队 c，再依次执行 b、c）
```

---

## Node.js 与 libuv：另一套 Loop（2009 至今）

### 历史背景

Node.js 没有 DOM、没有「渲染时机」，但有大量文件、网络、定时器等 I/O。因此它采用 **libuv** 驱动的 Event Loop，和 HTML 标准不是同一份实现。Node 的 Loop 被拆成**多个阶段**（phase）：timers → I/O 回调 → idle/prepare → poll（等待新 I/O）→ check（setImmediate）→ close 回调等。而且 Node 有 **process.nextTick**，它比「当前阶段的微任务」还要早，插在当前同步代码和当前阶段微任务之间，所以顺序是：**同步 → nextTick → 微任务（Promise 等）→ 下一阶段**。在 Node 里，`setTimeout(fn, 0)` 和 `setImmediate(fn)` 谁先要看你当前处于哪个阶段，二者顺序不保证；但 **nextTick 一定比同轮的 Promise 更早**。

### 标志性事件

- **2009 年**：Node.js 首次发布，libuv 作为跨平台异步 I/O 库被集成，Event Loop 多阶段模型确立。
- **2012 年前后**：`process.nextTick` 与 `setImmediate` 的语义被文档化，开发者开始区分「nextTick 是当前阶段立刻执行」「setImmediate 是 check 阶段」。
- **2015 年后**：Node 支持 ES6 Promise，微任务与 nextTick、各阶段的执行顺序成为常见面试题。
- **至今**：[Node.js Event Loop 官方文档](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick/) 详细描述各阶段，与浏览器 Event Loop 的对比成为必备知识。

### Node 各阶段一表速查

| 阶段大致顺序 | 做什么 | 常见 API |
|-------------|--------|----------|
| timers     | 执行到点的 setTimeout / setInterval 回调 | setTimeout, setInterval |
| pending    | 部分 I/O 的延迟回调                     | — |
| idle/prepare| 内部用                                 | — |
| poll        | 等待新 I/O、可阻塞                     | 多数异步 I/O 回调 |
| check       | 执行 setImmediate 回调                 | setImmediate |
| close       | 关闭回调（如 socket.on('close')）     | 各种 close 事件 |

同一阶段内顺序：**同步代码 → process.nextTick → 微任务（Promise 等）→ 下一阶段**。浏览器和 Node 的差异可以记一句：**浏览器看 HTML 标准，Node 看 libuv + Node 文档**，别混在一起背；面试时若被问到「Node 和浏览器的 Event Loop 有啥不同」，就答多阶段、nextTick、setImmediate 与 setTimeout(0) 顺序不保证即可。

**Node 里 setTimeout(fn, 0) 和 setImmediate(fn) 谁先？** 规范不保证。两者一个在 timers 阶段执行，一个在 check 阶段执行；若当前在主模块里同步执行，setImmediate 往往会在当前「这一轮」的 check 阶段跑，而 setTimeout(0) 可能要到下一轮 timers 才到点，所以有时 setImmediate 先；但在 I/O 回调里调用时，顺序又可能反过来。所以面试时答「不保证，看当前处于哪个阶段」即可，不必死记谁先谁后。

---

## 现代：async/await 与小结（2017 至今）

### 历史背景

**async/await**（ES2017）是基于 Promise 的语法糖：await 后面的代码相当于包在 `Promise.then` 里，所以**仍然是微任务**；async 函数里 await 之前的代码是同步的，会立刻进栈执行。理解 Event Loop 后，你就能解释：为什么「await 后面的逻辑总在当前同步代码和当前微任务清空之后、下一个宏任务之前」执行。requestAnimationFrame、requestIdleCallback 等则属于渲染与调度层面的 API，规范里不把它们算作 task 或 microtask，但执行时机大致在「微任务清空后、下一轮取宏任务前」附近，用于动画与低优先级任务。

### 标志性事件

- **2017 年**：ES2017 发布，async/await 成为标准，Promise + 微任务成为异步的绝对主流。
- **2018 年后**：`queueMicrotask()` 普及，微任务来源更加明确；各引擎与 Node 对 Event Loop 的实现与文档趋于稳定。
- **至今**：Event Loop 的「前世今生」成为前端/Node 面试的高频题，宏任务、微任务、nextTick、各阶段顺序是必背内容。

**为什么单线程 + 任务队列能撑到今天？** 一是历史原因：JS 出生在浏览器，多线程会带来 DOM 竞态、锁等复杂度，单线程 + 非阻塞 I/O 足够应对当时的交互。二是模型简单：一个调用栈、一个（后来多个）任务队列，心智负担小；真要并行可以交给 Web Worker 或 Node 的 worker_threads，主线程仍是一个 Loop。三是与渲染协同：浏览器可以在「清空微任务后、取下一个宏任务前」做布局和绘制，保证 60fps 的流畅度；若没有「微任务插队」，高优先级的 DOM 更新逻辑可能被一堆 setTimeout 拖后。

### 常见坑与面试题速记

- **setTimeout(fn, 0) 是立刻执行吗？** 不是。是「尽快」把 fn 放进宏任务队列，要等当前脚本 + 所有微任务跑完才会执行。
- **Promise 和 setTimeout 混在一起谁先？** 同轮里：then 先，setTimeout 后；记住「一个宏任务 → 清空微任务 → 再下一个宏任务」。
- **async/await 和 Event Loop 啥关系？** await 后面的代码等价于 then 回调，是微任务；await 之前的代码是同步的。
- **微任务里再塞微任务？** 可以；当前宏任务结束后会一直清微任务队列直到空，再取下一个宏任务；但别写死循环，否则会饿死宏任务、卡住渲染。
- **requestAnimationFrame 算宏任务还是微任务？** 规范里它不算二者，执行时机在渲染相关步骤，一般介于微任务清空后与下一宏任务前，用于动画。**requestIdleCallback** 则更靠后，在浏览器「空闲」时执行，适合做低优先级的统计、预加载等，不要放关键逻辑。

**宏任务 vs 微任务来源速查**（浏览器）：

| 类型     | 常见来源 |
|----------|----------|
| 宏任务   | 整段 script、setTimeout、setInterval、I/O、UI 事件（click、load 等） |
| 微任务   | Promise.then/catch/finally、queueMicrotask()、MutationObserver |

---

## 总结：一条时间线串起来

- **1995–2009**：同步世界，JS 诞生，无标准 Event Loop，只有简单事件与后来出现的定时器。
- **1997–2005**：定时器与 DOM 事件普及，任务队列雏形出现，尚无规范命名。
- **2005–2015**：AJAX 与 Node.js 让回调和异步 I/O 成为核心，回调地狱成痛；HTML5 规范逐步写入 Event Loop 与 task/microtask。
- **2015 至今**：Promise 与微任务定型，async/await 普及；浏览器看 HTML 标准，Node 看 libuv 多阶段 + nextTick；Event Loop 的「前世今生」成为必考必背。

**一轮 Loop 的图示小结**（浏览器）：可以想象成「调用栈 + 宏任务队列 + 微任务队列」三样东西。主线程只做一件事：从栈顶执行当前任务；当前任务（宏任务）执行完，栈空， then 把「微任务队列」里所有任务依次执行完；再根据需要做一次渲染；最后从「宏任务队列」里再取一个任务放进栈，周而复始。setTimeout、点击、网络回调都会往宏任务队列里塞；Promise.then、queueMicrotask 往微任务队列里塞。记住「一个宏任务 → 清空微任务 → 再下一个宏任务」，顺序题就不会乱。

**延伸阅读**：[HTML Standard - Event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)、[Timers and user prompts](https://html.spec.whatwg.org/dev/timers-and-user-prompts.html)；MDN [Event Loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/EventLoop) 与 [Microtask 指南](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide/In_depth)；[Node.js Event Loop](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick/)；Philip Roberts 的 "What the heck is the event loop anyway?" 视频。

**面试时如何一句话说清 Event Loop？** 可以答：JS 是单线程的，异步靠「任务队列」延后执行；浏览器里每轮取一个宏任务执行完，再清空所有微任务，再做渲染（如需），再取下一个宏任务，如此循环；Node 里用 libuv 多阶段 + nextTick + 微任务，顺序和浏览器略有不同。若对你有用，欢迎点赞、收藏或评论区一起串一串执行顺序题。
