# React 18 并发与 Reconciler 源码解析：Fiber、调度器与可中断渲染

> 从 Fiber 树、双缓冲、Scheduler 与 Lane 模型入手，解析 React 18 并发渲染与 Reconciler 的源码实现与调度策略。

---

## 一、背景：从栈协调到 Fiber

早期 React 的协调（Reconciler）是**递归、同步**的：从根组件开始，递归调用每个组件的 render，得到一棵「虚拟 DOM」树，再与上一棵对比（diff），最后把变更提交到真实 DOM。问题在于：一旦开始递归，就会一口气跑到底，无法暂停；若组件树很大，会长时间占用主线程，造成卡顿与掉帧。

**Fiber** 是 React 16 引入的「可中断的协调单元」。每个 Fiber 对应一个组件实例或 DOM 节点，是一个链表结构的节点，包含：type、key、child、sibling、return、pendingProps、memoizedState、alternate（指向另一棵树上对应节点，用于双缓冲）等。协调过程不再用递归栈，而是用 **循环 + 指针**：从根 Fiber 开始，若有 child 就向下，没有则找 sibling，再没有就 return 到父节点；每处理一个 Fiber 就检查「是否还有时间片」，没有则暂停并让出主线程，下次从当前节点继续。这样就把「大任务」拆成了「小步」，可与浏览器渲染、用户输入等穿插执行，实现**并发渲染**的基础。

## 二、Fiber 树与双缓冲

React 在内存中维护两棵 Fiber 树：**current**（当前已挂载到页面的树）和 **workInProgress**（正在构建的新树）。协调阶段是在 workInProgress 上进行的：从 current 克隆或新建 Fiber，根据本次更新计算新的 props/state 与子节点；全部完成后，把 workInProgress 一次性「提交」为新的 current，并更新 DOM。这种**双缓冲**避免在中间状态时直接改 DOM，保证视图在提交阶段才变化，且便于实现「并发下多次更新只提交一次」的语义。

**alternate** 指针：current 树上的 Fiber 的 alternate 指向 workInProgress 上对应节点，反之亦然。这样在「复用节点」时可以直接从 current 拷贝已有属性，只更新变化部分；在提交后，新的 current 就是原来的 workInProgress，下一轮更新再以它为 current 建新的 workInProgress。

## 三、Scheduler：时间片与优先级

「何时让出主线程」由 **Scheduler** 决定。Scheduler 是 React 仓库中的一个独立包，提供「按优先级调度任务」与「时间片」能力。在支持的环境下，它使用 **MessageChannel**（或 setTimeout）在每帧或每几毫秒让出控制权；同时维护一个**优先级队列**（通常用最小堆），高优先级任务（如用户输入）会先于低优先级任务（如数据预加载）执行。

**lane 模型**（React 17/18）：用二进制位表示「优先级通道」。不同更新会分配不同 lane（如 SyncLane、InputContinuousLane、DefaultLane）；同一批更新可能共用一个 lane。在协调时，会优先处理高 lane 的更新，并可**中断**低 lane 的工作以插入高 lane。Scheduler 的 **priority** 与 React 的 **lane** 会做映射，保证「用户交互」对应的更新能更快被处理。

## 四、Reconciler 的两阶段：render 与 commit

**render 阶段**（可中断）：从根 Fiber 开始，对每个 Fiber 执行 **beginWork**（根据 type 处理类组件、函数组件、HostComponent 等，计算子节点）和 **completeWork**（把子节点的变更汇总，处理 DOM 属性等）。整个过程是「深度优先」的：先向下到叶子，再向上 complete。在支持并发的模式下，render 可能执行到一半被高优先级更新打断，此时会丢弃当前 workInProgress 树的部分结果，从根重新开始处理高优先级更新。

**commit 阶段**（不可中断）：当 workInProgress 树构建完成，React 会进入 commit。commit 分三个子阶段：**beforeMutation**（执行 getSnapshotBeforeUpdate、useLayoutEffect 的销毁等）、**mutation**（把 Fiber 上的 DOM 变更应用到真实 DOM）、**layout**（执行 useLayoutEffect、componentDidMount/Update 等）。commit 必须同步执行完，否则会出现「视图与状态不一致」或 DOM 闪烁。

## 五、beginWork 与 completeWork 的职责

**beginWork(current, workInProgress, renderLanes)**：根据 workInProgress.tag（FunctionComponent、ClassComponent、HostRoot、HostComponent 等）分支处理。例如 FunctionComponent 会调用 `renderWithHooks` 得到 children，再 **reconcileChildren** 把 children 与 current 的子 Fiber 做 diff，生成新的子 Fiber 链表挂到 workInProgress.child。reconcileChildren 内部会调用 **reconcileChildFibers**，处理单节点、多节点的 key 复用与 placement/update/deletion 等 effectTag。

**completeWork(current, workInProgress)**：若为 HostComponent（原生 DOM），会创建或更新 DOM 节点，并把「属性变更」「子节点变更」记录在 Fiber 上（如 updateQueue），供 commit 的 mutation 阶段消费；若为其他类型则做状态汇总。全部 complete 后，根 Fiber 上会挂载完整的「effectList」或通过 subtree 可遍历到所有有 effect 的节点，供 commit 一次性应用。

## 六、并发模式下的中断与恢复

在 **Concurrent Mode** 或 **useTransition** 触发的更新中，render 阶段会周期性检查 **shouldYield**（Scheduler 提供）：若当前时间片用尽，则保存当前 workInProgress 的进度（即「当前处理到哪个 Fiber」），返回并让出主线程。下次调度到来时，从根重新开始，但会**复用已构建的 workInProgress 子树**（通过 bailout 或复用 alternate）以跳过未受本次更新影响的节点，从而在「可中断」与「不重复劳动」之间折中。

**优先级打断**：若在渲染低优先级更新的过程中，来了高优先级更新（如用户输入），React 会取消或暂停当前 workInProgress 的构建，先处理高优先级更新；低优先级更新可能稍后重新开始。这通过 lane 与 Scheduler 的优先级协同实现。

## 七、Hooks 与 Reconciler 的衔接

函数组件的 **Hooks**（useState、useEffect 等）在 **renderWithHooks** 中被调用。Hooks 的状态挂在 Fiber 的 **memoizedState** 上（一个链表，每个 Hook 对应一个节点）。useState 的更新会创建一个 **update** 对象（含 action、lane 等）并入队到 Hook 的 queue；在下次 render 时，会按顺序处理 queue 得到新 state。useEffect 的「副作用」会在 commit 的 layout 阶段之后，由 Scheduler 调度到异步执行（或 layout 阶段执行，取决于依赖与实现）；Reconciler 只负责在 Fiber 上标记 effect 链表，真正执行由 React 的 commit 流程与 Scheduler 配合完成。

## 八、Diff 策略与 key 的作用

Reconciler 在 **reconcileChildFibers** 中对「新 children」与「当前子 Fiber」做 diff。单节点时按 type 与 key 判断复用或新建；多节点时采用**双端比较**或**按 key 建立 Map 再遍历**的策略，尽量减少 DOM 的增删改。**key** 的作用是帮助 React 在「同一层级、兄弟之间」识别同一逻辑节点，从而复用 Fiber 与 DOM；key 不稳定会导致不必要的卸载与挂载，影响性能与状态保持。

## 九、useDeferredValue 与 useTransition 的调度语义

**useDeferredValue(value)**：返回一个「可能滞后于 value」的版本，React 会在空闲时把 deferred 值更新为 value，从而让高优先级渲染先完成，再在后台更新 deferred 触发的部分。**useTransition**：标记某次 setState 为「过渡更新」，其优先级低于紧急更新（如输入）；React 会先处理紧急更新再处理 transition，并可配合 **useTransition** 的 pending 状态做加载态。二者都依赖 Scheduler 的优先级与 lane，在源码中会为对应更新分配较低 lane，并在 render 时允许被高优先级打断。

## 十、源码关键路径

- **入口**：`react-reconciler` 的 `updateContainer`、`scheduleUpdateOnFiber`，最终进入 **performConcurrentWorkOnRoot** 或 **performSyncWorkOnRoot**。
- **render**：`workLoopConcurrent` / `workLoopSync` 循环调用 **performUnitOfWork**，内部是 **beginWork** + **completeUnitOfWork**（内含 completeWork）；子节点协调在 **reconcileChildFibers**。
- **Scheduler**：`scheduler` 包的 **workLoop**、**unstable_scheduleCallback**（按优先级入队）、**shouldYieldToHost**（时间片）。
- **commit**：`commitRoot` 中 **commitBeforeMutationEffects**、**commitMutationEffects**、**commitLayoutEffects**。

阅读时建议从一次 **setState** 或 **useState** 的更新出发，沿 **scheduleUpdateOnFiber → ensureRootIsScheduled → performWorkOnRoot → render 阶段 → commit 阶段** 走一遍，再结合 Fiber 树与 alternate 理解双缓冲。

## 总结

- React 18 的并发渲染建立在 **Fiber**（可中断的协调单元）与 **双缓冲**（current / workInProgress）之上；协调过程由递归改为循环，便于分片执行。
- **Scheduler** 负责时间片与优先级调度，**lane** 表示更新优先级，高优先级可打断低优先级的 render。
- **render 阶段**（beginWork + completeWork）可中断，**commit 阶段** 同步执行，保证 DOM 与副作用顺序一致。
- Hooks 的状态与 effect 挂在 Fiber 的 memoizedState 与 effect 链表上，与 Reconciler 的 render/commit 流程紧密配合。