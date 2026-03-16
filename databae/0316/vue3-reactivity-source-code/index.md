# Vue 3 响应式系统 Reactivity 源码深度解析：从 ref 到 effect 的完整链路

> 从 ref、reactive、effect、computed 到依赖收集与派发更新，逐层拆解 Vue 3 reactivity 模块的源码实现与设计取舍。

---

## 一、背景：为什么需要响应式

视图需要随数据变化而更新。若每次数据变更都手动调用「更新 DOM」的代码，会难以维护且易漏改。**响应式** 的目标是：声明「数据与视图的依赖关系」，当数据变化时自动执行副作用（如重新渲染）。Vue 3 把响应式抽成独立包 **@vue/reactivity**，可在无 DOM 环境中使用，也便于测试与复用。

核心概念可抽象为：

1. **响应式数据**：`ref`、`reactive`，其「读」会被记录为依赖，「写」会触发依赖更新。
2. **副作用**：`effect`（或渲染、computed 内部），在执行过程中会「读」响应式数据，从而建立「数据 → 该 effect」的依赖。
3. **依赖收集**：读时把当前 effect 记入数据的依赖集合（dep）。
4. **派发更新**：写时遍历该数据的 dep，重新执行其中注册的 effect。

Vue 3 用 **Proxy** 实现 `reactive`，用 **getter/setter + 对象** 实现 `ref`；依赖集合用 **Set** 存储 effect，避免重复。下面按「ref → reactive → effect → 依赖收集与派发 → computed」顺序，结合源码思路拆解。

## 二、ref：可包装任意值的引用

`ref(value)` 返回一个对象 `{ __v_isRef: true, value: ... }`，对 `.value` 的读会触发 **track**，写会触发 **trigger**。在源码（如 `packages/reactivity/src/ref.ts`）中：

- **RefImpl** 类持有 `_value`（若为对象可能转为 reactive）、`_rawValue`（原始值）、`dep`（一个 Dep 类型，实为 Set<ReactiveEffect>）。
- **get value()**：先 `trackRefValue(this)`，再返回 `_value`。
- **set value(v)**：若新值与旧值不同（或为 NaN 等特殊情况），则更新 `_value`，并 `triggerRefValue(this)`。

**trackRefValue(ref)** 会取「当前正在执行的 effect」（从全局或 TLS 的 `activeEffect`），若存在则把该 effect 加入 `ref.dep`，并把 `ref` 加入 effect 的依赖列表（用于后续清理）。**triggerRefValue(ref)** 会遍历 `ref.dep`，对每个 effect 执行调度（默认即执行 `effect.run()`，或通过 `scheduler` 放入微任务等）。

因此 **ref** 不依赖 Proxy，只依赖「当前 effect」的上下文与 Set 存储的依赖关系；适合包装基本类型或需要「整体替换」的引用。

## 三、reactive：基于 Proxy 的深响应式

`reactive(target)` 仅接受对象，返回其 **Proxy** 包装。对属性的读（get）、写（set）、遍历（ownKeys）、删除（deleteProperty）等都会拦截，并分别调用 **track** 与 **trigger**。源码在 `packages/reactivity/src/reactive.ts` 与 `baseHandlers.ts`（以及 `collectionHandlers.ts` 处理 Map/Set）。

**get 拦截**：若访问的是「可追踪」的属性（非 symbol、非 __v_ 开头等），则 `track(target, key)`；若子属性仍是对象，则递归 `reactive(child)` 并返回（避免重复包装同一对象用 **reactiveMap** 缓存）。**set 拦截**：先更新目标值，若 key 是新增的或值发生变化，则 `trigger(target, key, type)`。**track** 与 **trigger** 的 key 级别粒度，使「只读 a 不读 b」的 effect 在只改 b 时不会重新执行，实现细粒度更新。

**依赖存储结构**：全局有一个 **targetMap**（WeakMap<target, Map<key, Set<ReactiveEffect>>>）。track 时根据 target、key 找到或创建 Set，把 activeEffect 加入；trigger 时根据 target、key（及 type）找到 Set，遍历执行其中 effect。这样 reactive 的依赖是按「对象 + 属性」维度的，比 ref 的「整个 ref 一个 dep」更细。

## 四、effect：副作用的注册与执行

`effect(fn)` 会立即执行一次 `fn`；执行过程中对 ref/reactive 的读会触发 track，从而把当前 effect 记入对应 dep。之后当这些数据被写时，trigger 会再次执行该 effect（或通过 scheduler 调度）。在源码中（`effect.ts`）：

- **ReactiveEffect** 类封装了 `fn`、`scheduler`、`deps`（该 effect 依赖了哪些 dep，用于清理）、以及 `run()` 方法。
- **run()**：先清理该 effect 与所有 dep 的关联（避免过期依赖），设置 `activeEffect = this`，执行 `fn()`，最后清空 `activeEffect` 并返回结果。这样在 fn 执行期间的 track 都会把 this 加入对应 dep。
- **trigger** 时不是直接 `effect.run()`，而是可能走 **scheduler**；Vue 的渲染 effect 会设置 scheduler 为把更新放入微任务队列，实现批量更新。

**清理**：effect 的 `deps` 里存的是「依赖了我的 dep 的 Set」的引用；在 run 前会遍历 deps，从每个 Set 中移除自己，再清空 deps，然后重新执行 fn 并重新 track。这样可避免「已销毁的组件对应的 effect 仍被 trigger」的泄漏问题。

## 五、依赖收集（track）与派发更新（trigger）的细节

**track(target, key)**：从 targetMap 取 target 对应的 Map，再取 key 对应的 Set（没有则创建）；若存在 activeEffect，则把 activeEffect 加入该 Set，并把该 Set 加入 activeEffect.deps。**trigger(target, key, type)**：同样从 targetMap 取到 Set，但不会直接执行 run，而是构建一个 **effects 数组**（或使用新 Set 拷贝），避免在遍历时增删导致问题；然后对每个 effect 根据是否有 scheduler 调用 scheduler 或 run。

**effect 的递归与屏蔽**：若 effect 的 fn 里再次读同一数据并 trigger 自己，可能造成无限循环。Vue 通过「在 run 内再次 trigger 同一 effect 时跳过」或「用标志位禁止递归」等方式避免。具体实现中常有 `shouldTrack`、`effectStack` 等，用于区分「当前是首次执行还是被 trigger 触发」以及「是否允许 track」。

## 六、computed：带缓存的派生状态

`computed(getter)` 返回一个 **ComputedRefImpl**，其 `.value` 的读会执行 getter 并做依赖收集；只有在其依赖的数据变化时才会重新计算，否则返回缓存的 `_value`。实现上可以理解为：内部维护一个 **effect**，该 effect 的 fn 就是 getter；该 effect 有 **scheduler**，在依赖变化时只标记 dirty，不立刻重算。读 `.value` 时若 dirty 为 true 则执行 effect.run() 并缓存结果，否则直接返回缓存。

computed 的 effect 是 **lazy** 的：不会在创建时立即执行，只在第一次读 `.value` 时执行并 track。同时，computed 本身也会被 track：若另一个 effect 读了 computedRef.value，则该 effect 会依赖这个 computed 的 effect（或 computed 内部的 dep）；当 computed 的依赖变化导致 dirty 为 true 后，trigger 会触发依赖该 computed 的 effect，这些 effect 再读 .value 时就会触发 computed 的重新计算。这样形成正确的依赖链。

## 七、与 Vue 2 defineProperty 的对比

Vue 2 用 **Object.defineProperty** 做响应式：无法监听属性新增与数组下标，需要 `Vue.set` 或数组变异方法；且无法代理不存在的 key。Vue 3 的 Proxy 可以监听任意属性的 get/set/delete/ownKeys，对数组与动态 key 更自然。Proxy 是「懒」代理：只有被访问到的子对象才会被递归包装，而 defineProperty 常在初始化时递归整棵树。性能与内存上 Proxy 在大型对象上通常更优。Reflect 的使用则便于与 Proxy 的默认行为保持一致，便于转发与扩展。

## 八、shallowRef、readonly 与 watch 简述

**shallowRef**：只对 `.value` 的替换做响应式，不深度遍历 value；适合大对象「整体替换」场景，减少不必要的深度代理。**readonly**：对 reactive/ref 做只读包装，get 照常 track，set 时忽略或报错，便于向子组件传递不可变数据。**watch**：本质是创建一个 effect，其 fn 为「求值函数 + 回调」；当求值函数依赖的响应式数据变化时，effect 被 trigger，再根据新旧值决定是否执行回调；支持 immediate、deep 等选项，deep 通过递归遍历并「读」每个属性来收集依赖。

## 九、源码关键路径

- **ref**：`packages/reactivity/src/ref.ts` RefImpl、trackRefValue、triggerRefValue。
- **reactive**：`reactive.ts` reactive()、createReactiveObject；`baseHandlers.ts` 的 get/set；`collectionHandlers.ts` 的 Map/Set 代理。
- **effect**：`effect.ts` ReactiveEffect、effect()、run、track、trigger。
- **computed**：`computed.ts` ComputedRefImpl，内部 effect + dirty + scheduler。

阅读时建议从 `effect(fn)` 入手，看 run 时如何设置 activeEffect 与清理；再跟一次 track 与 trigger 的调用链，最后看 computed 如何用 effect + dirty 实现缓存。

## 总结

- Vue 3 响应式以 **ref**（get/set + dep）和 **reactive**（Proxy + targetMap）为核心；**effect** 通过 run 时设置 activeEffect 在 track 中建立「数据 → effect」的依赖。
- **trigger** 按 dep 集合执行 effect 的 run 或 scheduler，实现派发更新；computed 通过内部 effect + dirty 标志实现惰性求值与缓存。
- 与 Vue 2 的 defineProperty 相比，Proxy 在动态 key、数组与性能上更有优势；依赖结构按「对象+key」细粒度存储，便于精确更新。
