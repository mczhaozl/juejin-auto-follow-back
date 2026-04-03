# Vue 3 组合式 API 完全指南：从基础到实战

Vue 3 的组合式 API 是一个革命性的特性，它让代码组织更灵活、逻辑复用更方便。本文将带你全面掌握组合式 API。

## 一、为什么需要组合式 API

### 1. 选项式 API 的问题

```javascript
// 选项式 API
export default {
  data() {
    return {
      count: 0,
      name: 'Alice',
      todos: []
    }
  },
  computed: {
    doubleCount() {
      return this.count * 2
    }
  },
  methods: {
    increment() {
      this.count++
    },
    addTodo(text) {
      this.todos.push({ text, done: false })
    }
  },
  mounted() {
    this.fetchTodos()
  }
}
```

相关逻辑分散在不同选项中，难以复用。

### 2. 组合式 API 的优势

```javascript
import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const count = ref(0)
    const doubleCount = computed(() => count.value * 2)
    
    function increment() {
      count.value++
    }
    
    return { count, doubleCount, increment }
  }
}
```

逻辑可以组织在一起，易于复用。

## 二、响应式基础

### 1. ref

```javascript
import { ref } from 'vue'

const count = ref(0)
console.log(count.value) // 0

count.value++
console.log(count.value) // 1

const name = ref('Alice')
const active = ref(true)
```

### 2. reactive

```javascript
import { reactive } from 'vue'

const state = reactive({
  count: 0,
  name: 'Alice'
})

console.log(state.count) // 0
state.count++
console.log(state.count) // 1
```

### 3. ref vs reactive

```javascript
// 原始值用 ref
const count = ref(0)

// 对象用 reactive
const state = reactive({ count: 0 })

// 解构时保持响应式
import { toRefs, toRef } from 'vue'

const state = reactive({ count: 0, name: 'Alice' })
const { count, name } = toRefs(state)
const countRef = toRef(state, 'count')
```

## 三、计算属性

### 1. 基础计算属性

```javascript
import { ref, computed } from 'vue'

const firstName = ref('John')
const lastName = ref('Doe')

const fullName = computed(() => {
  return firstName.value + ' ' + lastName.value
})

console.log(fullName.value) // 'John Doe'
```

### 2. 可写计算属性

```javascript
const fullName = computed({
  get() {
    return firstName.value + ' ' + lastName.value
  },
  set(value) {
    const [f, l] = value.split(' ')
    firstName.value = f
    lastName.value = l
  }
})

fullName.value = 'Jane Smith'
console.log(firstName.value) // 'Jane'
```

## 四、侦听器

### 1. watch

```javascript
import { ref, watch } from 'vue'

const count = ref(0)

watch(count, (newValue, oldValue) => {
  console.log(`count changed from ${oldValue} to ${newValue}`)
})

count.value++
```

### 2. 侦听多个源

```javascript
const firstName = ref('John')
const lastName = ref('Doe')

watch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {
  console.log('Name changed')
})
```

### 3. 侦听响应式对象

```javascript
import { reactive, watch } from 'vue'

const state = reactive({ count: 0 })

watch(
  () => state.count,
  (newValue, oldValue) => {
    console.log(`count changed from ${oldValue} to ${newValue}`)
  }
)

watch(
  () => state,
  (newValue, oldValue) => {
    console.log('state changed')
  },
  { deep: true }
)
```

### 4. watchEffect

```javascript
import { ref, watchEffect } from 'vue'

const count = ref(0)

watchEffect(() => {
  console.log(`count is: ${count.value}`)
})

count.value++
```

## 五、生命周期钩子

```javascript
import { 
  onMounted, 
  onUpdated, 
  onUnmounted,
  onBeforeMount,
  onBeforeUpdate,
  onBeforeUnmount
} from 'vue'

export default {
  setup() {
    onMounted(() => {
      console.log('Component mounted')
    })
    
    onUpdated(() => {
      console.log('Component updated')
    })
    
    onUnmounted(() => {
      console.log('Component unmounted')
    })
  }
}
```

## 六、组合式函数 (Composables)

### 1. 简单的计数器

```javascript
// useCounter.js
import { ref, computed } from 'vue'

export function useCounter(initialValue = 0) {
  const count = ref(initialValue)
  const double = computed(() => count.value * 2)
  
  function increment() {
    count.value++
  }
  
  function decrement() {
    count.value--
  }
  
  function reset() {
    count.value = initialValue
  }
  
  return {
    count,
    double,
    increment,
    decrement,
    reset
  }
}
```

```javascript
// 使用
import { useCounter } from './useCounter'

export default {
  setup() {
    const { count, double, increment, decrement, reset } = useCounter(10)
    return { count, double, increment, decrement, reset }
  }
}
```

### 2. 数据获取

```javascript
// useFetch.js
import { ref, watchEffect } from 'vue'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)
  const isLoading = ref(true)
  
  async function fetchData() {
    isLoading.value = true
    error.value = null
    try {
      const response = await fetch(url)
      data.value = await response.json()
    } catch (e) {
      error.value = e
    } finally {
      isLoading.value = false
    }
  }
  
  watchEffect(() => {
    fetchData()
  })
  
  return { data, error, isLoading, refetch: fetchData }
}
```

```javascript
// 使用
import { useFetch } from './useFetch'

export default {
  setup() {
    const { data, error, isLoading, refetch } = useFetch('/api/users')
    return { data, error, isLoading, refetch }
  }
}
```

### 3. 本地存储

```javascript
// useLocalStorage.js
import { ref, watch } from 'vue'

export function useLocalStorage(key, initialValue) {
  const storedValue = localStorage.getItem(key)
  const data = ref(storedValue ? JSON.parse(storedValue) : initialValue)
  
  watch(data, (newValue) => {
    localStorage.setItem(key, JSON.stringify(newValue))
  })
  
  return data
}
```

```javascript
// 使用
import { useLocalStorage } from './useLocalStorage'

export default {
  setup() {
    const settings = useLocalStorage('settings', { theme: 'light' })
    return { settings }
  }
}
```

## 七、Script Setup 语法糖

```vue
<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const doubleCount = computed(() => count.value * 2)

function increment() {
  count.value++
}
</script>

<template>
  <button @click="increment">
    Count: {{ count }}, Double: {{ doubleCount }}
  </button>
</template>
```

## 八、最佳实践

1. 使用组合式函数封装逻辑
2. 合理使用 ref 和 reactive
3. 保持 setup 函数简洁
4. 善用组合式函数复用逻辑
5. 使用 TypeScript 增强类型安全

## 九、总结

Vue 3 组合式 API 带来了：
- 更灵活的代码组织
- 更好的逻辑复用
- 更好的 TypeScript 支持
- 更小的生产包体积

开始使用组合式 API，让你的 Vue 代码更优雅！
