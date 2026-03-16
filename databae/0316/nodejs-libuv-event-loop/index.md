# Node.js 事件循环与 libuv 源码剖析：从 V8 到多线程 I/O

> 结合 Node 与 libuv 源码，梳理事件循环各阶段、uv_run、线程池与 I/O 完成回调的完整调用链与调度策略。

---

## 一、背景：为什么需要事件循环

JavaScript 是单线程的：同一时刻只有一个执行上下文在跑。若所有 I/O（文件、网络、DNS）都做成同步阻塞，一次 `readFile` 就会卡住整个进程，无法处理其他请求。因此 Node.js 的设计是：**主线程只跑 JS 与协调逻辑，把耗时 I/O 交给系统或线程池，通过「事件循环」在 I/O 完成时把回调塞回主线程执行**。这样既保留单线程的简单心智，又获得高并发 I/O 能力。

事件循环的职责可以概括为：

1. **执行当前已就绪的 JavaScript**（包括定时器回调、I/O 回调等）。
2. **询问底层**：有没有新的 I/O 完成、定时器到期、或其它需要调度的任务？
3. **在「没有可执行 JS 且没有待处理 I/O」时** 适时阻塞或退出，避免空转。

Node.js 的底层 I/O 与事件循环由 **libuv** 提供：一个跨平台的异步 I/O 库，封装了 epoll（Linux）、kqueue（macOS/BSD）、IOCP（Windows）等，并提供了线程池处理「无法真正异步」的系统调用（如部分文件操作、 crypto、DNS）。理解 Node 的事件循环，本质就是理解 **libuv 的 uv_run** 与 **各阶段（phase）** 如何与 V8 的执行穿插在一起。

## 二、Node 与 libuv 的关系

Node.js 的 C++ 层（如 `src/node.cc`、`src/env.cc`）在启动时：

1. 初始化 V8 引擎与 Isolate。
2. 初始化 libuv：创建默认的 **uv_loop_t**（即我们常说的「一个事件循环」）。
3. 把需要周期性或在 I/O 完成时执行的逻辑，封装成 **uv_* 句柄**（handle）或 **uv_* 请求**（request），挂到 loop 上。
4. 在 `main()` 或 `RunBootstrapping` 之后调用 **uv_run(loop, UV_RUN_DEFAULT)**，进入事件循环；只有在没有活跃句柄和请求时，`uv_run` 才返回，进程随后退出。

因此，**一个 Node 进程对应一个 uv_loop_t**；所有 setTimeout、setImmediate、TCP 连接、文件读写，最终都会转化为对 libuv 的 handle/request 的注册与回调。Node 的 **process.nextTick** 与 **Promise 的 then** 不在 libuv 的 phase 里，而是由 Node 自己在每个「阶段」之间插入的 **nextTick 队列** 与 **microtask 队列** 处理，这是容易混淆的点，后文会细说。

## 三、事件循环各阶段（phase）

libuv 把一次「循环」拆成多个 **phase**，按固定顺序执行。Node 官方文档中的事件循环图描述的就是这些 phase 的先后关系（可能随 Node 版本有细微调整，以下以常见描述为准）：

1. **timers**：执行 `setTimeout`、`setInterval` 到期的回调。
2. **pending callbacks**：执行部分系统调用的回调（如 TCP 错误、某些 *nix 信号）。
3. **idle / prepare**：内部用，一般不在业务代码中直接接触。
4. **poll**：**核心阶段**。等待 I/O（网络、文件等）完成；若已有就绪 I/O，则执行其回调；同时会计算本次 poll 应阻塞多久（受 timers 中最近到期时间影响）。
5. **check**：执行 `setImmediate` 注册的回调。
6. **close callbacks**：执行关闭类句柄的回调（如 `socket.on('close')`）。

**一次 loop 的流程**：先跑 timers → pending → idle/prepare → **poll**（可能阻塞）→ check → close；然后若仍处于 RUN_DEFAULT 且还有活跃句柄，再回到 timers，周而复始。**process.nextTick** 与 **Promise** 不在上述 phase 中：Node 在「从 C++ 层回到 JS 执行」的边界处，先清空 nextTick 队列，再清空 microtask（Promise）队列，再继续当前 phase 或进入下一 phase。因此会出现「nextTick 先于 setImmediate」「Promise 先于 setTimeout」等现象。

## 四、uv_run 与一次 loop tick

在 libuv 源码中，**uv_run(uv_loop_t* loop, uv_run_mode mode)** 是事件循环的入口。其核心逻辑（简化）是：

```c
// 伪代码
while (runnable(loop)) {
  uv__update_time(loop);           // 更新 loop 的「当前时间」
  uv__run_timers(loop);            // timers phase
  uv__run_pending(loop);           // pending callbacks
  uv__run_idle(loop); uv__run_prepare(loop);
  uv__run_poll(loop, timeout);     // poll，可能阻塞
  uv__run_check(loop);             // check (setImmediate)
  uv__run_closing_handles(loop);   // close callbacks
  // ...
}
```

**runnable** 为 false 当且仅当：没有活跃的 handle、没有未完成的 request，或收到 stop 信号。**timeout** 在 poll 阶段用于「最多等多久」：若存在已到期的 timer，则 timeout 可为 0，使 poll 不阻塞；否则可能阻塞到下一个 timer 到期或 I/O 就绪。

在 Node 侧，每次进入某个 phase 执行 JS 回调时，会通过 **AsyncWrap** 或类似机制把「当前在哪个 phase」暴露给 C++；执行完一批 JS 后，会检查 nextTick 与 microtask 并执行，再回到 libuv 继续下一 phase。因此「phase 顺序」是 libuv 定的，「nextTick / microtask 插入时机」是 Node 绑定时定的。

## 五、线程池与异步 I/O

并非所有「异步」操作都由内核的 epoll/kqueue 完成。例如在 Linux 上，**文件读写**（如 `fs.readFile`）底层是同步系统调用；若在主线程执行会阻塞事件循环。因此 libuv 提供了一个 **线程池**（默认大小 4，可通过 `UV_THREADPOOL_SIZE` 环境变量调整，上限视平台而定）：把这类工作丢到线程池，在子线程中执行同步 I/O，完成后通过 **uv_async_t** 或类似机制通知主循环，主循环在 poll 或后续 phase 中执行回调。

涉及线程池的常见 API包括：文件系统（fs）、部分 crypto（如 pbkdf2）、部分 DNS（getaddrinfo 的同步路径）等。网络 I/O（TCP/UDP）则通常使用非阻塞 socket + epoll/kqueue，不占线程池。源码中，**uv_fs_*** 系列会封装 request，投递到线程池；**uv_work** 也可用于自定义的 CPU 密集或阻塞型任务。

线程池的实现是「固定数量的 worker 线程 + 任务队列」：主线程把任务入队，worker 取任务执行，完成后通过 **uv_async_send** 唤醒主循环，主循环在合适时机执行对应的完成回调。因此「异步」对调用方是统一的，底层可能是 epoll（网络）或线程池（文件等）。

## 六、poll 阶段的阻塞与唤醒

**poll** 是事件循环中唯一可能「长时间阻塞」的阶段。其职责有二：若存在已就绪的 I/O 回调，则执行它们（通过 `uv__io_poll` 或平台相关的 `epoll_wait`/`kqueue` 等）；若没有，则根据 **timeout** 决定阻塞多久，以便在定时器到期或新 I/O 就绪时唤醒。

timeout 的计算逻辑（简化）：若存在 **check 句柄**（setImmediate）或 **close 句柄**，则 timeout 可能为 0，避免阻塞；否则取「最近一个 timer 到期时间」与「默认值」中的较小值。这样既能让定时器按时触发，又能在无任务时避免忙等。在 Linux 上，`epoll_wait(epfd, events, maxevents, timeout)` 的 timeout 单位是毫秒；在 macOS 上 `kqueue` 的 `kevent` 也有超时参数。当超时到期或有 fd 就绪，poll 返回，事件循环继续到 check、close，再进入下一轮。

## 七、定时器与 setImmediate、nextTick

**setTimeout(fn, ms)** 在 libuv 中对应 **uv_timer_t**：在 timers phase 中，`uv__run_timers` 会遍历所有 timer，把已到期的回调交给 Node 执行（Node 再包装成 JS 调用）。**setImmediate** 对应 **uv_check_t**：在 check phase 执行。因此同一轮循环中，若 timer 已到期，会先执行 timer 再执行 setImmediate；若 timer 未到期，poll 可能阻塞到 timer 到期，然后下一轮先跑 timers 再跑 check。

**process.nextTick(callback)** 不由 libuv 管理：Node 维护一个 **nextTick 队列**，在「每次从 C++ 返回到 JS 执行完一段逻辑后」检查该队列并全部执行，再继续 phase 或 microtask。因此 nextTick 会「插队」到当前 phase 之后、下一 phase 之前，且会清空整队再往下，可能导致 nextTick 递归时饿死 I/O。

**Promise.then** 属于 **microtask**：在 JS 引擎（V8）层实现，Node 在每次「执行完一段 JS」后都会清空 microtask 队列（与浏览器一致）。所以顺序常为：nextTick → microtask（Promise）→ 当前 phase 的下一项或下一 phase。

## 八、与浏览器事件循环的差异

浏览器中同样有「任务队列 + microtask」：一次 task（如 setTimeout、I/O）执行完后会清空 microtask（Promise、MutationObserver），再取下一个 task。但浏览器没有 libuv 的「多 phase」划分，也没有线程池（Web Worker 是独立线程）。Node 的 **setImmediate** 在浏览器中不存在；浏览器的 **requestAnimationFrame** 与渲染周期绑定，Node 没有渲染。因此「Node 事件循环」与「浏览器事件循环」在「microtask 顺序」上一致，在「宏任务」的划分与顺序上不同，不能直接套用「先微后宏」的简单口诀，而要按 phase 理解。

## 九、源码关键路径（Node + libuv）

**Node 侧**：`src/node.cc` 的 `NodeMainInstance::Run()` 或类似入口会调用 `uv_run(env->event_loop(), UV_RUN_DEFAULT)`。定时器、setImmediate、nextTick 的绑定在 `src/env.cc`、`lib/timers.js`、`lib/internal/process/task_queues.js` 等；可搜索 `setTimeout`、`setImmediate`、`process.nextTick` 的 C++ 绑定与队列入队逻辑。

**libuv 侧**：`src/unix/core.c`（或 `src/win/core.c`）中的 `uv_run`；`src/unix/timer.c` 的 `uv__run_timers`；`src/unix/poll.c` 的 `uv__io_poll`（poll phase）；`src/threadpool.c` 的线程池与 `uv__work_done`。结合一次 `setTimeout` 或 `fs.readFile` 的调用栈，可以串起「JS → C++ binding → libuv handle/request → 回调回 JS」的完整路径。

## 总结

- Node.js 的事件循环由 **libuv** 的 `uv_run` 驱动，按 **timers → pending → idle/prepare → poll → check → close** 的顺序执行各 phase。
- **nextTick** 与 **Promise（microtask）** 由 Node/V8 在 phase 之间或回调之后插入，不在 libuv 的 phase 表中。
- 高并发 I/O 依赖 **非阻塞 socket + epoll/kqueue**（网络）与 **线程池**（文件、部分 crypto/DNS）；线程池完成通过异步通知回主循环执行回调。
- 阅读源码时，可从 `uv_run` 出发，沿各 `uv__run_*` 与 Node 的 C++ binding 对照文档中的事件循环图，理解「阶段顺序」与「nextTick/microtask 插入点」。
