# Vue3 响应式系统深度解析：ref、reactive 与 computed

> 深入讲解 Vue3 响应式系统原理，包括 ref、reactive、computed、watch 等，帮助你全面掌握 Vue3 的响应式编程。

## 一、ref 和 reactive

### 1.1 ref

```javascript
import { ref } from 'vue';

const count = ref(0);

console.log(count.value); // 0

count.value++;
console.log(count.value); // 1

// 在模板中自动解包
// <div>{{ count }}</div>
```

### 1.2 reactive

```javascript
import { reactive } from 'vue';

const state = reactive({
  name: '张三',
  age: 25
});

state.name = '李四';
console.log(state.name); // 李四
```

### 1.3 对比

| ref | reactive |
|-----|----------|
| 基础类型值 | 对象 |
| 需要 .value | 直接使用 |
| 可替换整个对象 | 不能替换 |

## 二、computed

### 2.1 基本用法

```javascript
import { ref, computed } from 'vue';

const firstName = ref('张');
const lastName = ref('三');

const fullName = computed(() => {
  return firstName.value + lastName.value;
});

console.log(fullName.value); // 张三
```

### 2.2 可写 computed

```javascript
const count = ref(1);
const plusOne = computed({
  get: () => count.value + 1,
  set: (val) => { count.value = val - 1; }
});

plusOne.value = 10;
console.log(count.value); // 9
```

## 三、watch

### 3.1 监听 ref

```javascript
import { ref, watch } from 'vue';

const count = ref(0);

watch(count, (newVal, oldVal) => {
  console.log(`变化: ${oldVal} → ${newVal}`);
});

count.value++; // 输出: 变化: 0 → 1
```

### 3.2 监听 reactive

```javascript
const state = reactive({ count: 0 });

watch(
  () => state.count,
  (newVal, oldVal) => {
    console.log(`变化: ${oldVal} → ${newVal}`);
  }
);
```

### 3.3 深度监听

```javascript
const state = reactive({
  user: { name: '张三' }
});

// 深度监听
watch(state, (newVal) => {
  console.log('变化:', newVal);
}, { deep: true });

// 立即执行
watch(state, () => {
  console.log('立即执行');
}, { immediate: true });
```

### 3.4 watchEffect

```javascript
watchEffect(() => {
  console.log('count 变化:', count.value);
});
```

## 四、响应式原理

### 4.1 Proxy

```javascript
const original = { name: '张三' };
const proxy = new Proxy(original, {
  get(target, key) {
    console.log('获取:', key);
    return Reflect.get(target, key);
  },
  set(target, key, value) {
    console.log('设置:', key, value);
    return Reflect.set(target, key, value);
  }
});

proxy.name = '李四'; // 设置: name 李四
console.log(proxy.name); // 获取: name
```

### 4.2 依赖收集

```javascript
class Dep {
  constructor() {
    this.subs = new Set();
  }
  
  depend() {
    if (activeEffect) {
      this.subs.add(activeEffect);
    }
  }
  
  notify() {
    this.subs.forEach(effect => effect());
  }
}
```

## 五、组合式函数

### 5.1 useCounter

```javascript
import { ref, computed } from 'vue';

function useCounter(initial = 0) {
  const count = ref(initial);
  
  const double = computed(() => count.value * 2);
  
  const increment = () => count.value++;
  const decrement = () => count.value--;
  
  return { count, double, increment, decrement };
}

const { count, double, increment } = useCounter();
```

### 5.2 useMouse

```javascript
import { ref, onMounted, onUnmounted } from 'vue';

function useMouse() {
  const x = ref(0);
  const y = ref(0);
  
  const update = (e) => {
    x.value = e.pageX;
    y.value = e.pageY;
  };
  
  onMounted(() => window.addEventListener('mousemove', update));
  onUnmounted(() => window.removeEventListener('mousemove', update));
  
  return { x, y };
}
```

### 5.3 useFetch

```javascript
import { ref } from 'vue';

function useFetch(url) {
  const data = ref(null);
  const loading = ref(true);
  const error = ref(null);
  
  fetch(url)
    .then(res => res.json())
    .then(json => { data.value = json; })
    .catch(err => { error.value = err; })
    .finally(() => { loading.value = false; });
  
  return { data, loading, error };
}
```

## 六、readonly 和 shallowRef

### 6.1 readonly

```javascript
import { readonly, reactive } from 'vue';

const state = reactive({ count: 0 });
const readonlyState = readonly(state);

readonlyState.count++; // 警告: 只能在 reactive 中修改
```

### 6.2 shallowRef

```javascript
import { shallowRef } from 'vue';

const state = shallowRef({ count: 0 });

state.value.count = 1; // 不触发响应
state.value = { count: 1 }; // 触发响应
```

## 七、实战案例

### 7.1 表单处理

```javascript
import { reactive, watch } from 'vue';

const form = reactive({
  username: '',
  email: '',
  password: ''
});

watch(form, (newVal) => {
  console.log('表单变化:', newVal);
}, { deep: true });
```

### 7.2 购物车

```javascript
import { reactive, computed } from 'vue';

const cart = reactive({
  items: []
});

const total = computed(() => {
  return cart.items.reduce((sum, item) => {
    return sum + item.price * item.quantity;
  }, 0);
});

function addItem(product) {
  const existing = cart.items.find(i => i.id === product.id);
  if (existing) {
    existing.quantity++;
  } else {
    cart.items.push({ ...product, quantity: 1 });
  }
}
```

## 八、总结

Vue3 响应式核心要点：

1. **ref**：基础类型响应式
2. **reactive**：对象响应式
3. **computed**：计算属性
4. **watch/watchEffect**：监听变化
5. **组合式函数**：复用逻辑
6. **readonly**：只读响应式
7. **shallowRef**：浅层响应式

掌握这些，Vue3 响应式不再难！

---

**推荐阅读**：
- [Vue3 响应式 API](https://vuejs.org/api/reactivity-core.html)

**如果对你有帮助，欢迎点赞收藏！**
