# Vuex 4 与 Pinia 完全指南：状态管理最佳实践

> 深入讲解 Vue 状态管理，包括 Vuex 4 的使用和 Pinia 的新方案，以及实际项目中的状态管理模式选择。

## 一、Vuex 4

### 1.1 安装

```bash
npm install vuex@4
```

### 1.2 创建 Store

```javascript
import { createStore } from 'vuex';

export default createStore({
  state: {
    count: 0,
    user: null
  },
  getters: {
    doubleCount: state => state.count * 2,
    isLoggedIn: state => !!state.user
  },
  mutations: {
    increment(state) {
      state.count++;
    },
    setUser(state, user) {
      state.user = user;
    }
  },
  actions: {
    async login({ commit }, credentials) {
      const user = await api.login(credentials);
      commit('setUser', user);
      return user;
    }
  }
});
```

### 1.3 使用

```javascript
import { useStore } from 'vuex';

export default {
  setup() {
    const store = useStore();
    
    const count = computed(() => store.state.count);
    const double = computed(() => store.getters.doubleCount);
    
    const increment = () => store.commit('increment');
    const login = () => store.dispatch('login', credentials);
    
    return { count, double, increment, login };
  }
}
```

## 二、Pinia

### 2.1 安装

```bash
npm install pinia
```

### 2.2 创建 Store

```javascript
import { defineStore } from 'pinia';

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0
  }),
  getters: {
    double: state => state.count * 2
  },
  actions: {
    increment() {
      this.count++;
    },
    async fetchData() {
      const data = await api.get();
      return data;
    }
  }
});
```

### 2.3 使用

```javascript
import { useCounterStore } from './stores/counter';

export default {
  setup() {
    const store = useCounterStore();
    
    const count = computed(() => store.count);
    const double = computed(() => store.double);
    
    store.increment();
    
    return { count, double };
  }
}
```

## 三、Pinia vs Vuex

### 3.1 对比

| 特性 | Pinia | Vuex |
|------|-------|------|
| TypeScript 支持 | 原生 | 一般 |
| API | 简洁 | 复杂 |
| 模块化 | 自动 | 手动 |
| 体积 | 更小 | 较大 |

## 四、实战案例

### 4.1 用户 Store

```javascript
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token')
  }),
  getters: {
    isLoggedIn: state => !!state.token
  },
  actions: {
    async login(credentials) {
      const { token, user } = await api.login(credentials);
      this.token = token;
      this.user = user;
      localStorage.setItem('token', token);
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
    }
  }
});
```

## 五、总结

Vue 状态管理核心要点：

1. **Vuex 4**：官方推荐方案
2. **Pinia**：新一代状态管理
3. **State**：状态定义
4. **Getters**：计算属性
5. **Mutations**：同步修改
6. **Actions**：异步操作

掌握这些，Vue 状态管理不再难！

---

**推荐阅读**：
- [Pinia 官方文档](https://pinia.vuejs.org/)

**如果对你有帮助，欢迎点赞收藏！**
