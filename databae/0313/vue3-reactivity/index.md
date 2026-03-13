# Vue 3 响应式完全指南：Ref、Reactive、Effect 与依赖收集原理

> 从 ref/reactive 用法到 effect、依赖收集、调度，再到与 Vue 2 的对比和迁移注意点，一篇搞懂 Vue 3 响应式。

---

## 一、这东西是什么

Vue 3 的响应式系统是一套**基于 Proxy 的依赖收集与触发机制**：你改「响应式数据」，依赖它的**副作用**（如渲染、watch、computed）会自动重新执行。和 Vue 2 的 `Object.defineProperty` 相比，能监听**动态增删属性**、**数组下标与 length**，并且 API 拆成 `ref`、`reactive`、`effect`、`computed` 等，更利于组合与 Tree-shaking。

**核心概念**：**reactive / ref**（声明响应式数据）、**effect**（依赖收集 + 副作用执行）、**依赖收集与触发**（get 时收集、set 时触发）。下文从用法到原理再到迁移，一条线讲完。

## 二、ref 与 reactive：怎么选

### 2.1 reactive

`reactive(obj)` 把普通对象变成响应式对象，**只能用于对象类型**（Object、Array、Map、Set 等）。访问和修改属性都会触发依赖收集与更新。

```javascript
import { reactive } from 'vue';

const state = reactive({ count: 0, list: [] });
state.count++;        // 触发依赖
state.list.push(1);   // 也会触发
state.newKey = 1;     // Vue 3 可监听新增属性，Vue 2 不行
```

**注意**：整个对象被「包」在 Proxy 里，若把对象**整体替换**（如 `state = reactive({ ... })`）会丢响应式；应改属性而不是换引用。

### 2.2 ref

`ref(initial)` 可以包**任意类型**（包括基本类型），通过 `.value` 读写。在模板里会自动解包，所以模板里不用写 `.value`。

```javascript
import { ref } from 'vue';

const count = ref(0);
count.value++;

const user = ref({ name: 'tom' });
user.value.name = 'jerry';
```

**为什么需要 ref**：JavaScript 里基本类型是按值传递的，没法用 Proxy 包一层；用 ref 就变成「包在一个对象里」，这样就能做依赖收集。对象也可以用 ref，这时 ref 内部对 `.value` 再包一层 reactive（等价于 `reactive(ref.value)`）。

### 2.3 怎么选

- **单值、基本类型、可能整体替换**：用 **ref**。
- **一组状态绑在一起、以对象形式存在**：用 **reactive**。
- **组合式函数里返回多个值**：通常返回一坨 ref，方便解构且保持响应式（若用 reactive 解构会丢响应式，除非 toRefs）。

## 三、effect 与依赖收集

**effect(fn)** 会立刻执行一次 `fn`；执行过程中对**响应式数据**的读取（get）会被记录，形成「fn 依赖这些数据」。之后这些数据一旦被写（set），就会**再次执行 fn**。渲染函数、`watch`、`computed` 底层都是基于 effect。

### 3.1 简易理解

```javascript
import { reactive, effect } from 'vue';

const state = reactive({ count: 0 });
effect(() => {
  console.log(state.count);  // 读：收集「这个 effect 依赖 state.count」
});
state.count++;  // 写：触发上面这个 effect 再跑一遍
```

**收集**：get 时把「当前正在执行的 effect」记到该属性的依赖列表里。  
**触发**：set 时把该属性的依赖列表里的 effect 都拿出来执行（或放进调度队列）。

### 3.2 调度（scheduler）

触发时可以不「立刻执行」effect，而是交给**调度器**（如放进微任务、或合并同一 tick 的多次触发）。Vue 的渲染更新就是通过调度器做的**异步批量更新**，避免同一轮里多次改数据导致多次渲染。

## 四、computed 与 watch

- **computed(getter)**：内部用 effect 跑 getter，并把结果缓存；只有依赖变了才重算，否则一直用缓存。
- **watch(source, cb)**：对 source 的依赖做 effect，依赖变时执行 cb；可配 `immediate`、`deep`、`flush`（时机）。

两者都建立在「依赖收集 + 触发」之上，区别是 computed 是「带缓存的派生值」，watch 是「副作用回调」。

## 五、与 Vue 2 的对比与迁移

| 点 | Vue 2 | Vue 3 |
|----|--------|------|
| 实现 | Object.defineProperty | Proxy |
| 动态增删属性 | 不支持（需 Vue.set） | 支持 |
| 数组下标/length | 部分 hack | 自然支持 |
| API | data、computed、watch 等选项 | ref、reactive、effect、computed、watch 组合式 |
| 解构 | 一般不会丢响应式（都在 data 上） | reactive 解构会丢，用 toRefs 或 ref |

**迁移注意**：用 `reactive` 时不要整体替换；需要解构时用 `toRefs(reactiveObj)` 转成多个 ref，或一开始就用多个 ref。

## 六、原理小结：依赖收集与触发的闭环

1. **reactive(obj)**：用 Proxy 包一层，get 时「收集当前 effect」，set 时「触发依赖该 key 的 effects」。
2. **ref(val)**：包成 `{ value: val }`，对 `.value` 做 get/set 的拦截，逻辑同上；若 val 是对象，一般再对 value 做 reactive。
3. **effect(fn)**：执行 fn 前把「当前 effect」设为全局/栈顶，fn 里对响应式数据的读就会把该 effect 记到对应 key 的依赖里；set 时取出这些 effect 执行或入队。

这样就把「数据 → 谁在用 → 数据变了通知谁」串起来了，也就是 Vue 3 响应式的核心闭环。

## 七、常见坑与最佳实践

- **reactive 整体替换**：会丢响应式，应改属性。
- **解构 reactive**：会变成普通变量，用 toRefs 或 ref。
- **循环里创建 ref/reactive**：可以，但要避免在循环里重复执行 reactive(同一引用)。
- **异步里改数据**：没问题，依赖会在下次 get 时重新收集；注意若在 effect 外改，要保证有 effect 读过该数据，否则不会触发视图更新。

## 八、总结

Vue 3 响应式 = **Proxy + ref/reactive + effect 依赖收集与触发**。会用 ref/reactive、知道何时用哪个、理解 effect 的收集与触发，就能在写组合式 API 和排查问题时心里有数。迁移 Vue 2 项目时重点注意「不要整体替换 reactive」和「解构用 toRefs」即可。

## 九、手写一个迷你版 reactive（帮助理解原理）

下面用几十行代码实现一个「能收集依赖、能触发更新」的迷你 reactive，便于把上面的概念具象化。

```javascript
const currentEffect = { current: null };
const depsMap = new WeakMap();  // target -> (key -> Set<effect>)

function track(target, key) {
  if (!currentEffect.current) return;
  let deps = depsMap.get(target);
  if (!deps) depsMap.set(target, (deps = new Map()));
  let set = deps.get(key);
  if (!set) deps.set(key, (set = new Set()));
  set.add(currentEffect.current);
}

function trigger(target, key) {
  const deps = depsMap.get(target)?.get(key);
  deps?.forEach(e => e());
}

function reactive(obj) {
  return new Proxy(obj, {
    get(target, key) {
      track(target, key);
      return Reflect.get(target, key);
    },
    set(target, key, value) {
      const ret = Reflect.set(target, key, value);
      trigger(target, key);
      return ret;
    },
  });
}

function effect(fn) {
  currentEffect.current = fn;
  fn();
  currentEffect.current = null;
}
```

用 `reactive` 包一个对象，再用 `effect` 包一段会读这个对象属性的函数，你就会在「改属性」时看到 effect 被重新执行。Vue 3 的源码里还有 ref、computed、调度、清理等，但**收集—触发**的骨架就是这样。

## 十、与 React 对比：为什么 Vue 不需要「手动依赖数组」

在 React 里，useEffect 要写依赖数组，否则容易闭包陈旧或过度执行。Vue 的 effect/watch 是**自动依赖收集**：你只要在 effect 里「读」用到的响应式数据，Vue 会记下来，下次这些数据变了再执行，不需要手写依赖数组。这是两种不同的设计取舍：Vue 用 Proxy 在运行时知道「谁读了谁」，React 用静态分析或人工声明依赖。理解这一点，能更好地区分两个生态的写法与心智负担。
