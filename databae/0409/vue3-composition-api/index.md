# Vue3 Composition API 深入指南：从入门到精通

> 全面解析 Vue3 Composition API 的核心概念，包括 ref、reactive、computed、watch 等，带你掌握 Vue3 的全新开发范式。

## 一、为什么需要 Composition API

### 1.1 Options API 的问题

```javascript
export default {
  data() { return { count: 0 } },
  computed: { double() { return this.count * 2 } },
  methods: { increment() { this.count++ } },
  mounted() { console.log('mounted') }
}
```

问题：逻辑分散在不同选项中，难以复用。

### 1.2 Composition API 优势

```javascript
import { ref, computed, onMounted } from 'vue';

export default {
  setup() {
    const count = ref(0);
    const double = computed(() => count.value * 2);
    
    function increment() { count.value++; }
    
    onMounted(() => console.log('mounted'));
    
    return { count, double, increment };
  }
}
```

优势：逻辑按功能组织，更易复用。

## 二、核心 API

### 2.1 ref - 响应式数据

```javascript
import { ref } from 'vue';

const count = ref(0);
console.log(count.value); // 读取
count.value = 10; // 修改
```

### 2.2 reactive - 对象响应式

```javascript
import { reactive } from 'vue';

const state = reactive({
  name: '张三',
  age: 25
});

state.name = '李四'; // 直接修改
```

### 2.3 computed - 计算属性

```javascript
import { ref, computed } from 'vue';

const firstName = ref('张');
const lastName = ref('三');

const fullName = computed(() => {
  return firstName.value + lastName.value;
});
```

### 2.4 watch - 监听器

```javascript
import { ref, watch } from 'vue';

const count = ref(0);

watch(count, (newVal, oldVal) => {
  console.log(`从 ${oldVal} 变为 ${newVal}`);
});

count.value = 1; // 触发 watch
```

## 三、生命周期

### 3.1 选项式 vs 组合式

| Options API | Composition API |
|-------------|----------------|
| created | onMounted |
| mounted | onMounted |
| updated | onUpdated |
| unmounted | onUnmounted |

### 3.2 使用示例

```javascript
import { onMounted, onUpdated, onUnmounted } from 'vue';

export default {
  setup() {
    onMounted(() => {
      console.log('组件挂载完成');
    });
    
    onUpdated(() => {
      console.log('组件更新完成');
    });
    
    onUnmounted(() => {
      console.log('组件卸载');
    });
  }
}
```

## 四、组件通信

### 4.1 props 和 emit

```javascript
// Parent.vue
import Child from './Child.vue';

export default {
  components: { Child },
  setup() {
    const msg = ref('Hello');
    return { msg };
  }
}
```

```vue
<!-- Child.vue -->
<script setup>
defineProps({ title: String });
defineEmits(['update']);
</script>

<template>
  <div>{{ title }}</div>
</template>
```

### 4.2 provide / inject

```javascript
// 父组件
import { provide } from 'vue';

export default {
  setup() {
    const data = ref('共享数据');
    provide('shared', data);
  }
}
```

```javascript
// 子组件
import { inject } from 'vue';

export default {
  setup() {
    const data = inject('shared');
    return { data };
  }
}
```

## 五、Composables

### 5.1 抽取逻辑

```javascript
// useMouse.js
import { ref, onMounted, onUnmounted } from 'vue';

export function useMouse() {
  const x = ref(0);
  const y = ref(0);
  
  function update(e) {
    x.value = e.pageX;
    y.value = e.pageY;
  }
  
  onMounted(() => window.addEventListener('mousemove', update));
  onUnmounted(() => window.removeEventListener('mousemove', update));
  
  return { x, y };
}
```

### 5.2 使用 Composable

```javascript
import { useMouse } from './useMouse';

export default {
  setup() {
    const { x, y } = useMouse();
    return { x, y };
  }
}
```

## 六、高级用法

### 6.1 readonly

```javascript
import { reactive, readonly } from 'vue';

const state = reactive({ count: 0 });
const readOnlyState = readonly(state);

// readOnlyState.count = 1; // 警告：只读
```

### 6.2 toRefs

```javascript
import { reactive, toRefs } from 'vue';

export function useState() {
  const state = reactive({ a: 1, b: 2 });
  
  return toRefs(state); // { a: ref, b: ref }
}
```

### 6.3 customRef

```javascript
import { customRef } from 'vue';

function useDebouncedRef(value, delay = 200) {
  return customRef((track, trigger) => {
    let timeout;
    return {
      get() {
        track();
        return value;
      },
      set(newValue) {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          value = newValue;
          trigger();
        }, delay);
      }
    };
  });
}
```

## 七、与 Options API 对比

### 7.1 数据定义

```javascript
// Options API
data() { return { count: 0 } }

// Composition API
const count = ref(0);
// 或
const state = reactive({ count: 0 });
```

### 7.2 方法定义

```javascript
// Options API
methods: { increment() { this.count++ } }

// Composition API
function increment() { count.value++; }
```

## 八、总结

Composition API 核心要点：

1. **ref / reactive**：响应式数据
2. **computed**：计算属性
3. **watch**：监听器
4. **生命周期**：onMounted 等
5. **Composables**：逻辑复用

掌握这些，你就能优雅地组织 Vue3 代码！

---

**推荐阅读**：
- [Vue3 官方文档](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Vue3 Composition API](https://vuejs.org/api/reactivity-core.html)

**如果对你有帮助，欢迎点赞收藏！**
