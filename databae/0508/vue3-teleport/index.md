# Vue 3 Teleport 完全指南

## 一、基础 Teleport

```vue
<template>
  <Teleport to="body">
    <div class="modal">
      <h2>模态框标题</h2>
      <button @click="close">关闭</button>
    </div>
  </Teleport>
</template>

<script setup>
const close = () => { /* */ };
</script>
```

## 二、模态框组件封装

```vue
<!-- Modal.vue -->
<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click="closeOverlay">
      <div class="modal" @click.stop>
        <slot name="header" />
        <slot name="body" />
        <slot name="footer" />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue']);

const closeOverlay = () => emit('update:modelValue', false);
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal { background: white; padding: 2rem; border-radius: 8px; }
</style>
```

## 三、使用模态框

```vue
<template>
  <button @click="showModal = true">打开模态框</button>
  <Modal v-model="showModal">
    <template #header><h3>确认</h3></template>
    <template #body><p>确定要执行此操作吗？</p></template>
    <template #footer>
      <button @click="showModal = false">取消</button>
      <button @click="confirm">确定</button>
    </template>
  </Modal>
</template>

<script setup>
import { ref } from 'vue';
import Modal from './Modal.vue';

const showModal = ref(false);
const confirm = () => { /* */ showModal.value = false; };
</script>
```

## 四、其他 Teleport 用例

```vue
<!-- 通知组件 -->
<template>
  <Teleport to="#notifications">
    <div class="notification">{{ message }}</div>
  </Teleport>
</template>

<!-- 加载指示器 -->
<Teleport to="body">
  <div v-if="loading" class="loading">加载中...</div>
</Teleport>
```

## 五、最佳实践

- 使用 body 或特定容器作为目标
- z-index 管理避免层叠问题
- 关闭时的事件处理
- 响应式设计
- 无障碍支持
- 动画过渡效果
