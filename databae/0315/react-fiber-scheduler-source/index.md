# React Fiber 调度器源码解析：从 workLoop 到 commit 的完整渲染链路

> 从 Scheduler、Fiber 树、workLoopConcurrent 到 commitRoot，拆解 React 18 可中断渲染与双缓冲的源码实现。

---

## 一、为什么要引入 Fiber

React 15 及之前， Reconciler 基于**递归**：从根组件一路向下调 `mount/update`，一旦开始就**跑到底**再提交 DOM。树大或组件重时，主线程长时间被占，导致输入卡顿、掉帧。**Fiber** 把「一棵组件树」拆成以** Fiber 节点**为单位的可调度工作单元：每个 Fiber 对应一个组件或 DOM 节点， Reconciler 按 Fiber 逐个处理，并可在每个单元结束后**让出主线程**，让高优先级更新（如用户输入）插队，从而实现**可中断的并发渲染**。

## 二、Fiber 节点与双缓冲

每个 Fiber 上保存了：**type**（组件类型或 DOM 标签）、**key**、**return / child / sibling**（树形链表结构）、**alternate**（指向另一棵树上对应节点，用于双缓冲）、**pendingProps / memoizedProps**、**memoizedState**、**flags**（增删改等副作用的标记）、**lanes**（优先级相关）等。**双缓冲**：当前屏对应一棵 **current** 树，正在计算的更新对应一棵 **workInProgress** 树；Reconciler 只改 workInProgress，算完后一次性 **commit** 把 workInProgress 换为 current，避免半成品 UI 暴露。

## 三、Scheduler 与优先级

React 的调度层 **Scheduler** 不依赖 React 自身：它维护一个**按优先级排序的任务队列**，在浏览器空闲时（或按时间片）执行任务，并可**取消/暂停**低优先级任务。React 把「一次更新」封装成 Scheduler 的 task，并赋予 **lane** 或 **expirationTime** 表示优先级；高优先级（如 input）会打断或抢占低优先级（如 list 渲染）。Scheduler 暴露 `scheduleCallback`、`cancelCallback`、`shouldYield` 等，Fiber 的 workLoop 里在每处理完一个单元后调用 `shouldYield()`，若需要让出则暂停并稍后继续。

## 四、workLoop 与 beginWork / completeWork

**workLoopConcurrent**（或 workLoopSync）从 root 开始，循环调用 **performUnitOfWork**：每次处理一个 Fiber。**performUnitOfWork** 内对当前 Fiber 调 **beginWork**（根据 tag 做 mount/update 的 diff、打 effect 标记、递归子节点），若没有子节点则 **completeUnitOfWork**，否则继续向下。**completeWork** 在「子节点都处理完」时执行：对 HostComponent 做 DOM 的增删改属性、对类组件做 ref 等；然后根据 **sibling** 找兄弟，没有则 **return** 到父节点再 complete。整棵 workInProgress 树就这样以**深度优先、先子后兄再父**的方式被遍历一遍，同时把 **effectList**（或依赖 flags 的 effect 链）串起来，供 commit 阶段消费。

## 五、commit 阶段：commitRoot

当 workLoop 把整棵 workInProgress 树算完，会调用 **commitRoot**。commit 阶段**不可中断**，分三个子阶段：**commitBeforeMutationEffects**（如 getSnapshotBeforeUpdate）、**commitMutationEffects**（对 DOM 增删改、执行 useLayoutEffect 的 destroy）、**commitLayoutEffects**（执行 useLayoutEffect 的 create、ref 回调、componentDidMount/Update）。之后把 **root.current 指向 workInProgress**，完成双缓冲切换；再在下一帧或微任务里触发 **useEffect** 的调度（异步）。这样保证用户看到的始终是「一整帧完整更新」，而不会看到半成品。

## 六、与 React 18 并发特性的关系

**useTransition**、**useDeferredValue** 和 **Suspense** 都建立在这套 Fiber + Scheduler 之上：过渡更新被标记为低优先级，可被高优先级打断；Suspense 的「挂起」会中断当前子树渲染并显示 fallback，等 Promise resolve 后再重新调度。理解 workLoop 的「可让出」和 commit 的「一次性提交」，就能更好理解并发模式下的行为与边界。

## 七、总结与阅读建议

Fiber = **可调度的工作单元 + 双缓冲 + 优先级**；Scheduler 负责「何时跑」、Reconciler 负责「怎么 diff」、commit 负责「怎么落 DOM」。读源码时建议从 **performSyncWorkOnRoot / performConcurrentWorkOnRoot** 入口跟到 **workLoop → beginWork/completeWork**，再跟 **commitRoot** 三子阶段；配合 React DevTools 的 Profiler 与「Highlight updates」观察优先级与打断效果，印象会更深。

## 八、关键数据结构与源码路径（React 18）

- **Fiber**：`packages/react-reconciler/src/ReactFiber.old.js` 中的 Fiber 类型定义；**FiberRoot** 在 `ReactFiberRoot.old.js`。
- **Scheduler**：`packages/scheduler/src/` 下 `Scheduler.js`（任务循环）、`SchedulerPriorities.js`（优先级常量）。
- **workLoop**：`packages/react-reconciler/src/ReactFiberWorkLoop.old.js` 的 `performConcurrentWorkOnRoot` / `performSyncWorkOnRoot`、`workLoopConcurrent`、`performUnitOfWork`。
- **beginWork / completeWork**：`ReactFiberBeginWork.old.js`、`ReactFiberCompleteWork.old.js`。
- **commit**：`ReactFiberCommitWork.old.js` 及 `commitRoot` 内对 mutation/layout 的遍历。

打开 React 仓库按上述路径跳转，再结合打断点单步，能快速对应到本文描述的流程。

## 九、常见问题

- **为什么我的 useEffect 执行了两次？** 在 React 18 Strict Mode 下会故意双调用于发现副作用问题；生产构建不会。
- **useTransition 没感觉变快？** 它不减少计算量，只是把更新标记为可打断，避免阻塞输入；若本身没有重计算，体感差异不大。
- **commit 阶段为什么不能打断？** 一旦改 DOM 就要原子完成，否则会出现半帧状态；只有「算 Fiber」阶段可让出。

## 十、调试与性能分析建议

在 Chrome DevTools 的 **Performance** 里录制一次交互，可看到主线程上 **Recalc Style**、**Layout**、**JS** 的占比；若 React 更新占大头，可再用 **React DevTools Profiler** 看是哪些组件 render 多、commit 耗时高。**Scheduler** 的 task 可在 Performance 的 JS 调用栈里看到 `workLoopConcurrent`、`performUnitOfWork` 等；结合 **Scheduling Profiler**（实验性）可观察任务优先级与打断。源码阅读时建议从 **createRoot** 或 **updateContainer** 跟到 **scheduleUpdateOnFiber**，再跟到 **ensureRootIsScheduled** 与 workLoop，这样能把「一次 setState 如何驱动整条链路」串起来，对理解并发与优先级大有帮助。

---