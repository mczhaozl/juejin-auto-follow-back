# JS Event Loop 前世今生：从「单线程苦力」到今天的调度大师

> 一文讲清 Event Loop 是什么、怎么来的、为啥长成现在这样；顺带手把手走一遍浏览器和 Node 里的差异，下次面试或调异步 bug 心里有数。

---

## 一、先搞清楚：Event Loop 到底是个啥

**一句话**：JavaScript 是单线程的，但又要处理点击、网络、定时器这些「晚点才发生」的事；**Event Loop** 就是引擎在「执行一段代码 → 看看有没有新任务 → 再执行」之间打转的那条循环，让你在只有一个线程的前提下，照样能「等」异步结果而不卡死页面。你可以把它想象成食堂阿姨：一次只打一份菜（当前任务），打完一份就看看队伍里还有谁（任务队列），再叫下一位；队伍里有人是「VIP」（微任务），阿姨会先把 VIP 全服务完再叫普通号。

三个关键词你肯定听过：**调用栈（Call Stack）**、**任务队列（Task Queue）**、**单线程非阻塞**。把三者串起来就是：主线程一次只干一件事（栈顶那一个），干完了就从队列里再取一件；队列里的任务来自定时器、事件、网络回调等，由宿主（浏览器或 Node）在「合适的时候」塞进去。所以 Event Loop 不是 JS 标准里的词，而是 **HTML 标准**（WHATWG）里对「浏览器里 JS 怎么被调度」的约定；ECMAScript 只管语法和执行语义，不管「什么时候跑哪段回调」——也就是说，**规范在别人家**，JS 自己只负责「上了跑道就拼命跑」。

---

## 二、前世（上）：没有 Loop 的日子

最早期的 JS，真的就是「一段脚本从头跑到尾」。没有 `setTimeout`，没有「点击以后再执行」的标准化方式；页面逻辑要么全写在一坨里，要么靠当时的浏览器各自扩展。那时候要是你想「过 3 秒再干某事」，要么没有标准 API，要么各厂实现五花八门。后来 **定时器 API** 出现了：`setTimeout` / `setInterval` 让「过一会儿再执行」变成可能。引擎的处境变成：当前代码跑着，同时要记住「还有一堆定时器在排队」；时间到了，总得有个地方把这些回调交回给 JS 执行——于是就有了**任务队列**的雏形：宿主环境把到点的定时器、触发的用户事件放进队列，JS 执行完当前代码后，就去队列里取下一个任务。这就是最原始的 **Loop**：取任务 → 执行 → 再取 → 再执行。**没有微任务，没有插队**，大家老老实实排队，先到先得。

那时候的问题很快就来了：**有些事需要「尽快」插队**。比如你改了一坨 DOM，希望在下一次画屏之前把依赖 DOM 的逻辑跑完，而不是等所有定时器、I/O 都排完队再说。又比如后来 Promise 出世了，大家希望「这个 then 最好立刻在当前任务屁股后面跑」，而不是被一堆 setTimeout 挤到后面。于是规范就开始琢磨：能不能给某些回调开个「快速通道」？

---

## 三、前世（下）：规范落地，Loop 有了「名字」和「VIP 通道」

**HTML5** 时代，WHATWG 在 [HTML Living Standard](https://html.spec.whatwg.org/dev/timers-and-user-prompts.html) 里把「事件循环」写进了规范，并且把「任务」拆得更细：一类是 **task**（后来大家常叫 macrotask，宏任务），比如整段 script、`setTimeout`/`setInterval`、I/O、UI 事件；另一类是 **microtask**（微任务），比如 Promise 的 then/catch/finally、`queueMicrotask()`、以及 DOM 的 `MutationObserver`。规范里规定：**每执行完一个宏任务，就要把当前已有的微任务队列全部清空**，再考虑渲染、再取下一个宏任务。这样，Promise 回调就能抢在「下一个 setTimeout」甚至「下一次渲染」之前执行，高优先级异步有了着落——也就是上面说的「VIP 通道」。

所以「前世」可以简单记成：**先有单线程 + 任务队列（定时器、事件），再在规范里给 Loop 起名、引入微任务，形成今天浏览器里「一个宏任务 → 一车微任务 → 渲染（如需）→ 下一个宏任务」的节奏。** 微任务不是后来「打补丁」打的，而是规范设计里就定好的「每轮必清」的队列，专门用来收 Promise、queueMicrotask 这些「急着跑」的回调。

---

## 四、今生：一轮 Loop 到底怎么转

下面这段可以当口诀背（**浏览器**环境）：

1. **取一个宏任务**（例如一段 script、或一个 setTimeout 回调）执行到底；
2. **栈空之后**，把当前 **微任务队列** 里能跑的全跑完（包括 then、queueMicrotask、MutationObserver）；
3. 若需要 **渲染**，就在此时做（约 60fps 的节奏）；
4. 回到步骤 1，取下一个宏任务。

于是就有了那道经典题：`setTimeout(fn, 0)` 和 `Promise.resolve().then(fn)` 谁先？答案是：**当前这段同步代码算一个宏任务**；它跑完以后，会先清空微任务（所以 Promise 的 then 先），再取下一个宏任务（所以 setTimeout 后）。微任务可以在「同一个宏任务」结束后立刻插队，宏任务不行。面试官问「0 毫秒不是立刻吗」——对，是「立刻进队列」，但「出队」要等当前宏任务 + 所有微任务都跑完，所以 then 还是更早。

```javascript
console.log("1");
setTimeout(() => console.log("2"), 0);
Promise.resolve().then(() => console.log("3"));
console.log("4");
// 输出：1 4 3 2
```

顺序就是：同步 1、4 → 微任务 3 → 下一个宏任务 2。

---

## 五、Node.js 来了：另一套 Loop，另一片江湖

Node 没有 DOM、没有「渲染时机」，但有大量 I/O 和定时器；所以它用的是 **libuv** 驱动的 Event Loop，和 HTML 标准不是同一份。Node 的 Loop 分**多个阶段**（phase）：timers（到点的 setTimeout/setInterval）→ I/O 回调 → idle/prepare → poll（等新 I/O）→ check（setImmediate）→ 关闭回调等。而且 Node 有 **process.nextTick**，它比「当前阶段的微任务」还早，专门插在当前同步代码和当前阶段微任务之间，所以顺序是：**同步 → nextTick → 微任务（Promise 等）→ 下一阶段**。在 Node 里写 `setTimeout(fn, 0)` 和 `setImmediate(fn)` 谁先，要看你当前在哪个阶段，二者不一定谁先谁后；而 `process.nextTick` 一定比同轮的 Promise 更早，所以 nextTick 名字里的「next」其实是「当前栈清空后立刻下一个」，不是「下一个阶段」。

所以「前世今生」在 Node 这边多了一条线：**从「类浏览器」的简单队列，到 libuv 多阶段 + nextTick + 微任务**，为的是更好地服务 I/O 密集、无 UI 的场景。浏览器和 Node 的差异可以记一句：**浏览器看 HTML 标准，Node 看 libuv + Node 文档**，别混在一起背。

**Node 各阶段一表速查**（方便你对着文档再啃一遍）：

| 阶段大致顺序 | 做什么 | 常见 API |
|-------------|--------|----------|
| timers     | 执行到点的 setTimeout / setInterval 回调 | setTimeout, setInterval |
| pending    | 部分 I/O 的延迟回调                     | — |
| idle/prepare| 内部用，不必背                         | — |
| poll        | 等新 I/O、可阻塞                       | 多数异步 I/O 回调 |
| check       | 执行 setImmediate 回调                 | setImmediate |
| close       | 关闭回调（如 socket.on('close')）     | 各种 close 事件 |

同一阶段内：**同步代码 → process.nextTick → 微任务（Promise 等）→ 下一阶段**。所以 nextTick 是「当前阶段内、栈清空后立刻执行」，不跨阶段。

---

## 六、手把手：用一段代码把「一轮 Loop」走一遍

下面这段在**浏览器**里跑，你可以自己试：

```javascript
console.log("A");
setTimeout(() => console.log("B"), 0);
queueMicrotask(() => console.log("C"));
Promise.resolve()
  .then(() => console.log("D"))
  .then(() => console.log("E"));
console.log("F");
// 输出：A F C D E B
```

- **宏任务 1**：整段 script。先打 A、F；然后微任务队列里有 C、D 的回调（E 要等 D 执行完再 then 进去）。
- **清微任务**：C → D（D 执行完把 E 推进微任务队列）→ E。
- **宏任务 2**：setTimeout 回调，打 B。

所以顺序就是 A F C D E B。若你把 `queueMicrotask` 和 Promise 当成「同一层」的微任务，只记住「当前宏任务结束后，把微任务队列清空再往下」就不会乱。再练一题：如果中间加一句 `setTimeout(() => console.log("X"), 0)`，X 和 B 谁先？——看谁先被推进队列；同一轮里两个 0ms 的 setTimeout 通常按代码顺序入队，所以一般还是 B 先 X 后，但规范不保证 0ms 的精确顺序，只保证「不会比当前宏任务 + 微任务更早」。

---

## 六点五、常见坑与面试题速记

- **「setTimeout(fn, 0) 是立刻执行吗」**：不是。是「尽快」把 fn 放进宏任务队列，要等当前脚本 + 所有微任务跑完才会轮到它；所以常用来「把逻辑推迟到本轮末尾」。
- **「Promise 和 setTimeout 混在一起谁先」**：同轮里，then 先、setTimeout 后；记住「一个宏任务 → 清空微任务 → 再下一个宏任务」。
- **「async/await 和 Event Loop 啥关系」**：await 后面的代码相当于包在「Promise.then」里，所以是微任务；async 函数里 await 之前的代码是同步的，一执行就进栈。
- **「微任务里再塞微任务」**：可以。当前宏任务结束后，会一直清微任务队列，**直到队列空**；所以你在 then 里再 then、再 queueMicrotask，都会在这一轮里依次跑完，然后才取下一个宏任务。但别写死循环往里塞，否则会饿死宏任务、卡住渲染。
- **「requestAnimationFrame 算宏任务还是微任务」**：规范里它不在「任务」里，而是在**渲染前**的某个时机执行，一般介于「微任务清空后」和「下一次取宏任务前」之间，用来做动画最合适；不要指望它和 setTimeout 的顺序，各浏览器略有差异。

---

## 七、为啥要长成现在这样：简单小结

- **单线程**：历史包袱 + 简单模型，避免锁、竞态，适合 UI 和脚本场景；真要并行可以开 Worker，那是另一条线程、另一套消息机制。
- **任务队列**：让定时器、事件、网络在不阻塞主线程的前提下「延后执行」，宿主负责在合适的时机把回调塞进队列。
- **微任务**：在「当前宏任务」和「下一个宏任务/渲染」之间插队，满足 Promise、DOM 变更后逻辑等高优先级需求；规范明说「每轮宏任务后清空微任务」，所以 then 总比 setTimeout 更「贴」当前代码。
- **Node 多阶段 + nextTick**：为服务端 I/O 和调度优化，和浏览器同源不同体；nextTick 是 Node 自己的「超 VIP」，不跟 Promise 抢同一条队。

---

## 八、延伸与推荐

- **规范**：[HTML Standard - Event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)、[Timers and user prompts](https://html.spec.whatwg.org/dev/timers-and-user-prompts.html)；MDN 的 [Event Loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/EventLoop) 与 [Microtask 指南](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide/In_depth)。
- **Node**：[The Node.js Event Loop](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick/) 官方文档。
- **经典视频**：Philip Roberts 的 "What the heck is the event loop anyway?"（一搜就有），把栈、队列、Loop 画得很清楚。

Event Loop 的「前世」是单线程 + 队列 + 规范里有了名字和微任务；「今生」是浏览器里「宏任务 → 微任务 → 渲染」的固定节奏，加上 Node 那边 libuv 多阶段与 nextTick 的扩展。搞清这两条线，写异步、调顺序、答面试题就都能对上号了。如果对你有用，欢迎点赞、收藏或评论区一起串一串执行顺序题。
