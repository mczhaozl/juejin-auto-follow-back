# Vue 3 响应式原理深度解析：从 Proxy 到 Ref 的完整实现

Vue 3 的响应式系统是其最核心的特性之一。本文将带你从底层原理到完整实现，全面理解 Vue 3 的响应式系统。

## 一、响应式系统的演变

### 1. Vue 2 vs Vue 3

```javascript
// Vue 2: Object.defineProperty
const obj = {};
let value = 0;
Object.defineProperty(obj, 'count', {
  get() {
    console.log('Get:', value);
    return value;
  },
  set(newValue) {
    console.log('Set:', newValue);
    value = newValue;
  }
});

obj.count = 1;  // Set: 1
console.log(obj.count);  // Get: 1

// 问题：
// - 无法检测对象属性的添加/删除
// - 无法检测数组索引和长度的变化
// - 需要递归遍历整个对象

// Vue 3: Proxy
const obj = { count: 0 };
const proxy = new Proxy(obj, {
  get(target, prop, receiver) {
    console.log('Get:', prop);
    return Reflect.get(target, prop, receiver);
  },
  set(target, prop, value, receiver) {
    console.log('Set:', prop, value);
    return Reflect.set(target, prop, value, receiver);
  }
});

proxy.count = 1;  // Set: count 1
console.log(proxy.count);  // Get: count

// 优势：
// - 可以拦截对象属性的添加/删除
// - 可以拦截数组索引和长度变化
// - 懒代理：只在访问时才代理
// - 支持 Map/Set/WeakMap/WeakSet
```

## 二、核心概念

### 1. 依赖收集和触发更新

```
1. 读取属性 → track() → 收集依赖
2. 修改属性 → trigger() → 触发更新
```

### 2. 简化版实现

```javascript
// 存储副作用函数
let activeEffect = null;
const targetMap = new WeakMap();

// 副作用函数
function effect(fn) {
  activeEffect = fn;
  fn();
  activeEffect = null;
}

// 依赖收集
function track(target, key) {
  if (!activeEffect) return;
  
  let depsMap = targetMap.get(target);
  if (!depsMap) {
    targetMap.set(target, (depsMap = new Map()));
  }
  
  let deps = depsMap.get(key);
  if (!deps) {
    depsMap.set(key, (deps = new Set()));
  }
  
  deps.add(activeEffect);
}

// 触发更新
function trigger(target, key) {
  const depsMap = targetMap.get(target);
  if (!depsMap) return;
  
  const deps = depsMap.get(key);
  if (deps) {
    deps.forEach(effect => effect());
  }
}

// 响应式对象
function reactive(obj) {
  return new Proxy(obj, {
    get(target, key, receiver) {
      track(target, key);
      return Reflect.get(target, key, receiver);
    },
    set(target, key, value, receiver) {
      const oldValue = target[key];
      const result = Reflect.set(target, key, value, receiver);
      if (oldValue !== value) {
        trigger(target, key);
      }
      return result;
    }
  });
}

// 使用
const state = reactive({ count: 0 });

effect(() => {
  console.log('Count:', state.count);
});

state.count = 1;  // 输出: Count: 1
state.count = 2;  // 输出: Count: 2
```

## 三、完整实现：@vue/reactivity

### 1. effect 函数

```typescript
type EffectFn = () => void;

let activeEffect: EffectFn | null = null;
const effectStack: EffectFn[] = [];

interface ReactiveEffectOptions {
  lazy?: boolean;
  scheduler?: (fn: EffectFn) => void;
}

class ReactiveEffect {
  deps: Set<ReactiveEffect>[] = [];
  active = true;
  
  constructor(
    public fn: EffectFn,
    public scheduler: EffectFn | null = null
  ) {}
  
  run() {
    if (!this.active) {
      return this.fn();
    }
    try {
      effectStack.push(this);
      activeEffect = this;
      return this.fn();
    } finally {
      effectStack.pop();
      activeEffect = effectStack[effectStack.length - 1] || null;
    }
  }
  
  stop() {
    if (this.active) {
      cleanupEffect(this);
      this.active = false;
    }
  }
}

function cleanupEffect(effect: ReactiveEffect) {
  effect.deps.forEach(dep => {
    dep.delete(effect);
  });
  effect.deps.length = 0;
}

function effect(fn: EffectFn, options: ReactiveEffectOptions = {}) {
  const _effect = new ReactiveEffect(fn, options.scheduler);
  
  if (!options.lazy) {
    _effect.run();
  }
  
  const runner = _effect.run.bind(_effect) as any;
  runner.effect = _effect;
  
  return runner;
}
```

### 2. track 和 trigger

```typescript
type Dep = Set<ReactiveEffect>;
type KeyToDepMap = Map<any, Dep>;
const targetMap = new WeakMap<any, KeyToDepMap>();

function track(target: object, key: unknown) {
  if (!activeEffect) return;
  
  let depsMap = targetMap.get(target);
  if (!depsMap) {
    targetMap.set(target, (depsMap = new Map()));
  }
  
  let dep = depsMap.get(key);
  if (!dep) {
    depsMap.set(key, (dep = new Set()));
  }
  
  trackEffects(dep);
}

function trackEffects(dep: Dep) {
  if (activeEffect) {
    dep.add(activeEffect);
    activeEffect.deps.push(dep);
  }
}

function trigger(target: object, key: unknown, newValue?: unknown) {
  const depsMap = targetMap.get(target);
  if (!depsMap) return;
  
  const deps = depsMap.get(key);
  if (deps) {
    triggerEffects(deps);
  }
}

function triggerEffects(dep: Dep) {
  const effects = [...dep];
  for (const effect of effects) {
    if (effect !== activeEffect) {
      if (effect.scheduler) {
        effect.scheduler();
      } else {
        effect.run();
      }
    }
  }
}
```

### 3. reactive 实现

```typescript
const isObject = (val: unknown): val is object =>
  val !== null && typeof val === 'object';

const enum ReactiveFlags {
  SKIP = '__v_skip',
  IS_REACTIVE = '__v_isReactive',
  RAW = '__v_raw'
}

const reactiveMap = new WeakMap();

function createReactiveObject(
  target: object,
  proxyMap: WeakMap<object, object>,
  baseHandlers: ProxyHandler<object>,
  collectionHandlers: ProxyHandler<object>
) {
  if (!isObject(target)) {
    return target;
  }
  
  if (target[ReactiveFlags.RAW] || proxyMap.has(target)) {
    return target;
  }
  
  const proxy = new Proxy(
    target,
    baseHandlers
  );
  
  proxyMap.set(target, proxy);
  return proxy;
}

const baseHandlers: ProxyHandler<object> = {
  get(target, key, receiver) {
    if (key === ReactiveFlags.IS_REACTIVE) {
      return true;
    }
    if (key === ReactiveFlags.RAW) {
      return target;
    }
    
    const res = Reflect.get(target, key, receiver);
    
    track(target, key);
    
    if (isObject(res)) {
      return reactive(res);
    }
    
    return res;
  },
  
  set(target, key, value, receiver) {
    const oldValue = target[key as keyof typeof target];
    const hadKey = Array.isArray(target)
      ? Number(key) < target.length
      : key in target;
    
    const result = Reflect.set(target, key, value, receiver);
    
    if (!hadKey) {
      trigger(target, key, value);
    } else if (value !== oldValue) {
      trigger(target, key, value);
    }
    
    return result;
  },
  
  deleteProperty(target, key) {
    const hadKey = key in target;
    const result = Reflect.deleteProperty(target, key);
    if (hadKey) {
      trigger(target, key);
    }
    return result;
  },
  
  has(target, key) {
    track(target, key);
    return Reflect.has(target, key);
  },
  
  ownKeys(target) {
    track(target, Array.isArray(target) ? 'length' : Symbol.iterator);
    return Reflect.ownKeys(target);
  }
};

function reactive<T extends object>(target: T): T {
  return createReactiveObject(target, reactiveMap, baseHandlers, {} as any) as T;
}

function isReactive(value: unknown): boolean {
  return !!(value && (value as any)[ReactiveFlags.IS_REACTIVE]);
}

function toRaw<T>(observed: T): T {
  const raw = observed && (observed as any)[ReactiveFlags.RAW];
  return raw ? toRaw(raw) : observed;
}
```

### 4. ref 实现

```typescript
class RefImpl<T> {
  private _value: T;
  private _rawValue: T;
  
  public dep?: Dep = undefined;
  public readonly __v_isRef = true;
  
  constructor(value: T) {
    this._rawValue = value;
    this._value = convert(value);
  }
  
  get value() {
    trackRefValue(this);
    return this._value;
  }
  
  set value(newVal) {
    if (newVal !== this._rawValue) {
      this._rawValue = newVal;
      this._value = convert(newVal);
      triggerRefValue(this);
    }
  }
}

function convert<T>(value: T): T {
  return isObject(value) ? reactive(value) : value;
}

function trackRefValue(ref: RefImpl<any>) {
  if (activeEffect) {
    trackEffects(ref.dep || (ref.dep = new Set()));
  }
}

function triggerRefValue(ref: RefImpl<any>) {
  if (ref.dep) {
    triggerEffects(ref.dep);
  }
}

function ref<T>(value: T): Ref<T> {
  return new RefImpl(value) as any;
}

function isRef<T>(r: Ref<T> | unknown): r is Ref<T> {
  return !!(r && (r as any).__v_isRef);
}

function unref<T>(ref: T | Ref<T>): T {
  return isRef(ref) ? ref.value : ref;
}

function proxyRefs<T extends object>(objectWithRefs: T) {
  return new Proxy(objectWithRefs, {
    get(target, key, receiver) {
      return unref(Reflect.get(target, key, receiver));
    },
    set(target, key, value, receiver) {
      const oldValue = target[key as keyof T];
      if (isRef(oldValue) && !isRef(value)) {
        oldValue.value = value;
        return true;
      }
      return Reflect.set(target, key, value, receiver);
    }
  });
}
```

### 5. computed 实现

```typescript
class ComputedRefImpl<T> {
  private _value!: T;
  private _dirty = true;
  
  public readonly effect: ReactiveEffect;
  public readonly __v_isRef = true;
  public dep?: Dep = undefined;
  
  constructor(getter: () => T) {
    this.effect = new ReactiveEffect(getter, () => {
      if (!this._dirty) {
        this._dirty = true;
        triggerRefValue(this);
      }
    });
  }
  
  get value() {
    if (this._dirty) {
      this._value = this.effect.run()!;
      this._dirty = false;
    }
    trackRefValue(this);
    return this._value;
  }
}

function computed<T>(getter: () => T): ComputedRef<T> {
  return new ComputedRefImpl(getter) as any;
}
```

### 6. watch 实现

```typescript
function watch<T>(
  source: (() => T) | Ref<T> | T extends object ? T : never,
  cb: (newValue: T, oldValue: T) => void,
  options: { immediate?: boolean; deep?: boolean } = {}
) {
  let getter: () => T;
  
  if (isRef(source)) {
    getter = () => source.value;
  } else if (isReactive(source)) {
    getter = () => traverse(source);
  } else {
    getter = source as () => T;
  }
  
  let oldValue: T;
  let newValue: T;
  
  const job = () => {
    newValue = effect.run()!;
    if (options.deep || newValue !== oldValue) {
      cb(newValue, oldValue);
      oldValue = newValue;
    }
  };
  
  const effect = new ReactiveEffect(getter, job);
  
  if (options.immediate) {
    job();
  } else {
    oldValue = effect.run()!;
  }
}

function traverse(value: unknown, seen = new Set()) {
  if (!isObject(value) || seen.has(value)) {
    return value;
  }
  seen.add(value);
  if (Array.isArray(value)) {
    for (let i = 0; i < value.length; i++) {
      traverse(value[i], seen);
    }
  } else {
    for (const key in value) {
      traverse(value[key as keyof typeof value], seen);
    }
  }
  return value;
}
```

## 四、完整示例

```typescript
import { reactive, ref, computed, effect, watch } from './reactivity';

// 响应式对象
const state = reactive({
  count: 0,
  name: 'Vue 3'
});

// ref
const count = ref(0);

// computed
const doubleCount = computed(() => count.value * 2);

// effect
effect(() => {
  console.log('Count changed:', count.value);
  console.log('Double count:', doubleCount.value);
});

// watch
watch(
  () => state.count,
  (newVal, oldVal) => {
    console.log(`State count changed from ${oldVal} to ${newVal}`);
  }
);

// 测试
count.value = 1;
// 输出:
// Count changed: 1
// Double count: 2

count.value = 2;
// 输出:
// Count changed: 2
// Double count: 4

state.count = 10;
// 输出: State count changed from 0 to 10
```

## 五、Vue 3 组件中的响应式

```vue
<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue';

const count = ref(0);
const state = reactive({
  message: 'Hello',
  todos: []
});

const doubleCount = computed(() => count.value * 2);
const todoCount = computed(() => state.todos.length);

function increment() {
  count.value++;
}

function addTodo(text) {
  state.todos.push({ text, done: false });
}

watch(count, (newVal, oldVal) => {
  console.log(`count: ${oldVal} → ${newVal}`);
});

watch(() => state.todos.length, (newVal) => {
  console.log(`Todo count: ${newVal}`);
});

onMounted(() => {
  console.log('Component mounted');
});
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <p>Double: {{ doubleCount }}</p>
    <button @click="increment">Increment</button>
    
    <p>{{ state.message }}</p>
    <p>Todos: {{ todoCount }}</p>
    <button @click="addTodo('New todo')">Add Todo</button>
  </div>
</template>
```

## 六、核心优化

### 1. 懒代理

```typescript
// Vue 3：只在访问属性时才递归代理
const state = reactive({
  a: {
    b: {
      c: 1
    }
  }
});

// 访问 state.a 时才代理 state.a
// 访问 state.a.b 时才代理 state.a.b
```

### 2. 浅层响应式

```typescript
function shallowReactive<T extends object>(target: T): T {
  // 只代理第一层，深层对象不代理
  return createReactiveObject(
    target,
    shallowReactiveMap,
    shallowHandlers,
    {} as any
  ) as T;
}

const shallowHandlers = {
  get(target, key) {
    track(target, key);
    return target[key];  // 不递归 reactive
  },
  set(target, key, value) {
    // ...
  }
};
```

### 3. 只读响应式

```typescript
function readonly<T extends object>(target: T): Readonly<T> {
  return createReactiveObject(
    target,
    readonlyMap,
    readonlyHandlers,
    {} as any
  ) as Readonly<T>;
}

const readonlyHandlers = {
  get(target, key) {
    track(target, key);
    return target[key];
  },
  set() {
    console.warn('Cannot set property on readonly object');
    return false;
  },
  deleteProperty() {
    console.warn('Cannot delete property on readonly object');
    return false;
  }
};
```

## 七、总结

Vue 3 响应式系统核心要点：
- 使用 Proxy 而非 Object.defineProperty
- WeakMap 存储依赖关系（targetMap → depsMap → dep）
- track() 收集依赖，trigger() 触发更新
- effect() 注册副作用函数
- reactive() 处理对象，ref() 处理基本类型
- computed() 计算属性，watch() 监听器
- 懒代理、浅层响应式、只读响应式优化

理解响应式原理，让你更好地使用和优化 Vue 3 应用！
