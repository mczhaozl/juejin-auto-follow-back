# Vue 3 v-model 完全指南

## 一、基础用法

```vue
<!-- 父组件 -->
<script setup>
import { ref } from 'vue';
const message = ref('Hello');
</script>

<template>
  <CustomInput v-model="message" />
</template>

<!-- 子组件 -->
<script setup>
const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue']);
</script>

<template>
  <input 
    :value="props.modelValue" 
    @input="emit('update:modelValue', $event.target.value)" 
  />
</template>
```

## 二、v-model 参数

```vue
<!-- 父组件 -->
<script setup>
import { ref } from 'vue';
const title = ref('My Title');
const count = ref(0);
</script>

<template>
  <Child 
    v-model:title="title" 
    v-model:count="count" 
  />
</template>

<!-- 子组件 -->
<script setup>
const props = defineProps(['title', 'count']);
const emit = defineEmits(['update:title', 'update:count']);
</script>
```

## 三、自定义修饰符

```vue
<script setup>
const props = defineProps({
  modelValue: String,
  modelModifiers: {
    default: () => ({})
  }
});
const emit = defineEmits(['update:modelValue']);

function handleInput(e) {
  let value = e.target.value;
  if (props.modelModifiers.capitalize) {
    value = value.charAt(0).toUpperCase() + value.slice(1);
  }
  emit('update:modelValue', value);
}
</script>

<template>
  <input :value="props.modelValue" @input="handleInput" />
</template>
```

## 四、组合式 v-model

```tsx
// useVModel 工具
import { computed } from 'vue';

export function useVModel(props, key, emit) {
  return computed({
    get() {
      return props[key];
    },
    set(value) {
      emit(`update:${key}`, value);
    }
  });
}
```

## 最佳实践
- 优先使用 v-model 简化双向绑定
- 多个绑定使用 v-model:argument
- 自定义修饰符处理通用逻辑
- 保持子组件的简洁性
