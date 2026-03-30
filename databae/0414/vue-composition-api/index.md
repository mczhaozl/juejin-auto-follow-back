# Vue3 Composition API 完全指南：深入理解 setup

> 深入讲解 Vue3 Composition API，包括 setup 函数、响应式系统、生命周期钩子组合，以及复用逻辑的最佳实践。

## 一、setup

### 1.1 基本用法

```javascript
import { ref, computed } from 'vue';

export default {
  setup() {
    const count = ref(0);
    const doubled = computed(() => count.value * 2);
    
    const increment = () => {
      count.value++;
    };
    
    return { count, doubled, increment };
  }
}
```

### 1.2 Props

```javascript
export default {
  props: {
    title: String
  },
  setup(props) {
    console.log(props.title);
  }
}
```

### 1.3 Context

```javascript
import { useContext } from 'vue';

export default {
  setup(props, context) {
    const { attrs, slots, emit } = context;
    
    emit('update', data);
  }
}
```

## 二、响应式

### 2.1 ref 和 reactive

```javascript
import { ref, reactive } from 'vue';

const count = ref(0);
const state = reactive({
  name: '张三',
  age: 18
});

// ref 需要 .value
count.value++;
state.age++;
```

### 2.2 toRefs

```javascript
import { reactive, toRefs } from 'vue';

const state = reactive({
  name: '张三',
  age: 18
});

const { name, age } = toRefs(state);
```

## 三、生命周期

### 3.1 钩子注册

```javascript
import { onMounted, onUpdated, onUnmounted } from 'vue';

export default {
  setup() {
    onMounted(() => {
      console.log('组件挂载');
    });
    
    onUpdated(() => {
      console.log('组件更新');
    });
    
    onUnmounted(() => {
      console.log('组件卸载');
    });
  }
}
```

### 3.2 完整生命周期

| Vue 2 | Vue 3 |
|-------|-------|
| created | setup |
| mounted | onMounted |
| updated | onUpdated |
| destroyed | onUnmounted |

## 四、逻辑复用

### 4.1 Composables

```javascript
// useCounter.js
import { ref, computed } from 'vue';

export function useCounter(initial = 0) {
  const count = ref(initial);
  const doubled = computed(() => count.value * 2);
  
  const increment = () => count.value++;
  const decrement = () => count.value--;
  
  return { count, doubled, increment, decrement };
}

// 使用
import { useCounter } from './useCounter';

export default {
  setup() {
    const { count, increment } = useCounter(10);
    return { count, increment };
  }
}
```

## 五、总结

Vue3 Composition API 核心要点：

1. **setup**：入口函数
2. **ref**：基本响应式
3. **reactive**：对象响应式
4. **生命周期**：onMounted 等
5. **Composables**：逻辑复用

掌握这些，Vue3 开发更得心应手！

---

**推荐阅读**：
- [Vue3 官方文档](https://vuejs.org/api/)

**如果对你有帮助，欢迎点赞收藏！**
