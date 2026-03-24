# 布尔变量不加 is 前缀？这不是坑人吗

> 探讨布尔变量命名规范：为什么有人反对 is 前缀，以及如何在实际项目中做出合理选择。

---

## 目录 (Outline)
- [一、争议的起源](#一争议的起源)
- [二、支持 is 前缀的理由](#二支持-is-前缀的理由)
- [三、反对 is 前缀的理由](#三反对-is-前缀的理由)
- [四、实际项目中的困境](#四实际项目中的困境)
- [五、折中方案](#五折中方案)
- [六、各大项目的实践](#六各大项目的实践)
- [七、推荐规范](#七推荐规范)
- [八、常见布尔前缀](#八常见布尔前缀)
- [九、实战建议](#九实战建议)

---

## 一、争议的起源

在代码规范中，经常看到这样的建议：

```
❌ 不推荐：isLoading, isDisabled, isVisible
✅ 推荐：loading, disabled, visible
```

理由是：

- 更简洁
- 避免冗余
- 符合某些语言习惯

但很多开发者觉得：**这不是坑人吗？没有 is 前缀怎么知道是布尔值？**

## 二、支持 is 前缀的理由

### 1. 语义明确

```javascript
// ❌ 不清楚类型
const loading = getStatus();
const disabled = checkPermission();

// ✅ 一眼看出是布尔值
const isLoading = getStatus();
const isDisabled = checkPermission();
```

### 2. 避免歧义

```javascript
// ❌ visible 可能是数字（可见度）或字符串（可见状态）
const visible = element.style.opacity;

// ✅ isVisible 明确是布尔值
const isVisible = element.style.display !== 'none';
```

### 3. 代码可读性

```javascript
// ❌ 读起来不自然
if (loading) { ... }
if (disabled) { ... }

// ✅ 读起来像英语句子
if (isLoading) { ... }
if (isDisabled) { ... }
```

### 4. IDE 提示友好

```javascript
// 输入 is 后，IDE 会列出所有布尔变量
const isLoading = true;
const isDisabled = false;
const isVisible = true;

// 输入 is... 自动补全
```

## 三、反对 is 前缀的理由

### 1. 冗余

```javascript
// ❌ 冗余
const isButtonDisabled = button.disabled;

// ✅ 简洁
const disabled = button.disabled;
```

### 2. 某些语言习惯

```python
# Python 习惯不加 is
if loading:
    pass

# Ruby 习惯用 ?
if loading?
    pass
```

### 3. 属性命名

```javascript
// ❌ HTML 属性不用 is
<button disabled>Click</button>

// ❌ React props 也不用 is
<Button disabled loading />

// 所以变量也不用？
const disabled = true;
const loading = false;
```

### 4. 类型系统已经标注

```typescript
// TypeScript 已经标注类型，不需要 is
const loading: boolean = false;
const disabled: boolean = true;
```

## 四、实际项目中的困境

### 场景 1：React 组件 props

```typescript
// 方案 A：props 不加 is，内部变量加 is
interface ButtonProps {
  disabled?: boolean;
  loading?: boolean;
}

function Button({ disabled, loading }: ButtonProps) {
  const isDisabled = disabled || loading;
  const isLoading = loading;
  
  return <button disabled={isDisabled}>...</button>;
}

// 方案 B：统一不加 is
interface ButtonProps {
  disabled?: boolean;
  loading?: boolean;
}

function Button({ disabled, loading }: ButtonProps) {
  const actuallyDisabled = disabled || loading;
  
  return <button disabled={actuallyDisabled}>...</button>;
}
```

### 场景 2：状态管理

```javascript
// ❌ 不一致
const state = {
  loading: false,
  isError: false,
  disabled: true,
  hasData: false
};

// ✅ 统一加 is
const state = {
  isLoading: false,
  isError: false,
  isDisabled: true,
  hasData: false // has/can 等也是布尔前缀
};
```

### 场景 3：函数返回值

```javascript
// ❌ 不清楚返回类型
function checkAuth() {
  return user !== null;
}

// ✅ 函数名暗示返回布尔值
function isAuthenticated() {
  return user !== null;
}
```

## 五、折中方案

### 1. 根据上下文决定

```javascript
// 组件 props：不加 is（遵循 HTML/React 习惯）
<Button disabled loading />

// 内部变量：加 is（提升可读性）
const isDisabled = disabled || loading;

// 函数：加 is/has/can（明确返回布尔值）
function isValid() { return true; }
function hasPermission() { return true; }
function canEdit() { return true; }
```

### 2. 团队统一规范

```javascript
// 规范 1：所有布尔变量都加前缀
const isLoading = false;
const hasData = true;
const canEdit = false;

// 规范 2：只有容易混淆的加前缀
const loading = false; // 不会混淆
const isValid = true; // valid 可能是字符串，加前缀
```

### 3. 用 TypeScript 类型标注

```typescript
// 类型已经说明是布尔值，可以不加 is
const loading: boolean = false;

// 但函数返回值建议加 is
function isLoading(): boolean {
  return state.loading;
}
```

## 六、各大项目的实践

### React

```javascript
// React 源码：props 不加 is
<input disabled readOnly required />

// 但内部变量会加
const isDisabled = props.disabled;
```

### Vue

```javascript
// Vue 3 源码：混合使用
const isReactive = (value) => { ... }
const readonly = (target) => { ... }
```

### Ant Design

```typescript
// props 不加 is
interface ButtonProps {
  disabled?: boolean;
  loading?: boolean;
  danger?: boolean;
}
```

### Lodash

```javascript
// 函数名加 is
_.isArray([1, 2, 3]); // true
_.isString('hello'); // true
```

## 七、推荐规范

### 1. 变量命名

```javascript
// ✅ 推荐：加 is/has/can 等前缀
const isLoading = false;
const hasData = true;
const canEdit = false;

// ⚠️ 例外：组件 props 遵循平台习惯
<Button disabled loading />
```

### 2. 函数命名

```javascript
// ✅ 返回布尔值的函数必须加前缀
function isValid(value) { return true; }
function hasPermission(user) { return true; }
function canAccess(resource) { return true; }

// ❌ 不要这样
function valid(value) { return true; }
function check(value) { return true; }
```

### 3. 类/接口属性

```typescript
// ✅ 类属性加前缀
class User {
  isActive: boolean;
  hasPermission: boolean;
}

// ⚠️ 接口属性看情况
interface ButtonProps {
  disabled?: boolean; // 遵循 HTML 习惯
}

interface UserState {
  isLoggedIn: boolean; // 内部状态加前缀
}
```

## 八、常见布尔前缀

| 前缀 | 含义 | 示例 |
|------|------|------|
| is | 是否 | isLoading, isVisible, isValid |
| has | 拥有 | hasData, hasPermission, hasError |
| can | 能否 | canEdit, canDelete, canAccess |
| should | 应该 | shouldUpdate, shouldRender |
| will | 将要 | willUnmount, willUpdate |
| did | 已经 | didMount, didUpdate |

## 九、实战建议

### 1. 新项目

```javascript
// 统一规范：所有布尔变量加前缀
const isLoading = false;
const hasData = true;
const canEdit = false;

// 例外：组件 props 遵循平台习惯
<Button disabled loading />
```

### 2. 老项目

```javascript
// 保持一致性，不要混用
// ❌ 不要这样
const loading = false;
const isError = true;
const hasData = false;

// ✅ 统一风格
const isLoading = false;
const isError = true;
const hasData = false;
```

### 3. ESLint 规则

```javascript
// .eslintrc.js
module.exports = {
  rules: {
    // 要求布尔变量加前缀
    '@typescript-eslint/naming-convention': [
      'error',
      {
        selector: 'variable',
        types: ['boolean'],
        format: ['PascalCase'],
        prefix: ['is', 'has', 'can', 'should', 'will', 'did']
      }
    ]
  }
};
```

## 总结

布尔变量要不要加 is 前缀？

支持加的理由：

- 语义明确，一眼看出是布尔值
- 避免歧义，提升可读性
- IDE 提示友好

反对加的理由：

- 冗余，不够简洁
- 某些语言/框架习惯不加
- TypeScript 已有类型标注

推荐做法：

- 变量：加前缀（isLoading, hasData, canEdit）
- 函数：必须加前缀（isValid, hasPermission）
- 组件 props：遵循平台习惯（disabled, loading）
- 团队统一规范，保持一致性

最重要的是：**团队内部保持一致**，不要混用。如果团队已有规范，遵循即可；如果是新项目，建议加前缀以提升可读性。
