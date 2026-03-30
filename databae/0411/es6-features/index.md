# ES6+ 核心新特性完全指南

> 全面介绍 ES6 到 ES2023 的核心新特性，包括箭头函数、解构赋值、Promise、async/await、装饰器等现代 JavaScript 必备知识。

## 一、let 和 const

### 1.1 let

```javascript
let count = 0;
count = 1; // OK

// 块级作用域
if (true) {
  let block = 'inside';
}
console.log(block); // Error: block is not defined
```

### 1.2 const

```javascript
const PI = 3.14159;
// PI = 3; // Error: Assignment to constant variable

// 对象的引用不变
const user = { name: '张三' };
user.name = '李四'; // OK
```

## 二、箭头函数

### 2.1 基本语法

```javascript
// 传统函数
function add(a, b) {
  return a + b;
}

// 箭头函数
const add = (a, b) => a + b;

const double = x => x * 2;
```

### 2.2 this 绑定

```javascript
// 传统方式
function Timer() {
  this.time = 0;
  setInterval(function() {
    this.time++; // this 指向 window
  }, 1000);
}

// 箭头函数
function Timer() {
  this.time = 0;
  setInterval(() => {
    this.time++; // this 指向 Timer 实例
  }, 1000);
}
```

## 三、解构赋值

### 3.1 数组解构

```javascript
const [a, b, c] = [1, 2, 3];
// a=1, b=2, c=3

const [first, ...rest] = [1, 2, 3, 4];
// first=1, rest=[2,3,4]

const [a, , c] = [1, 2, 3];
// a=1, c=3
```

### 3.2 对象解构

```javascript
const { name, age } = { name: '张三', age: 25 };
// name='张三', age=25

const { name: userName } = { name: '张三' };
// userName='张三'

const { id = 'default' } = { name: '张三' };
// id='default'
```

## 四、模板字符串

### 4.1 基本用法

```javascript
const name = '张三';
const age = 25;

// 传统方式
const message = '我叫' + name + ', 今年' + age + '岁';

// 模板字符串
const message = `我叫${name}, 今年${age}岁`;
```

### 4.2 多行和函数

```javascript
const html = `
  <div>
    <h1>${name}</h1>
    <p>${age}</p>
  </div>
`;

// 带函数
const tag = (strings, ...values) => {
  console.log(strings, values);
};

tag`Hello ${name}!`;
```

## 五、Promise

### 5.1 基本用法

```javascript
const promise = new Promise((resolve, reject) => {
  setTimeout(() => {
    resolve('Success!');
  }, 1000);
});

promise
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

### 5.2 链式调用

```javascript
fetch('/api/user')
  .then(res => res.json())
  .then(user => fetch(`/api/posts/${user.id}`))
  .then(res => res.json())
  .then(posts => console.log(posts))
  .catch(error => console.error(error));
```

### 5.3 Promise.all

```javascript
const promises = [
  fetch('/api/users'),
  fetch('/api/posts'),
  fetch('/api/comments')
];

Promise.all(promises)
  .then(([users, posts, comments]) => {
    console.log(users, posts, comments);
  });
```

## 六、async/await

### 6.1 基本语法

```javascript
async function getData() {
  try {
    const res = await fetch('/api/data');
    const data = await res.json();
    return data;
  } catch (error) {
    console.error(error);
  }
}
```

### 6.2 并行执行

```javascript
async function getData() {
  const [users, posts] = await Promise.all([
    fetch('/api/users').then(r => r.json()),
    fetch('/api/posts').then(r => r.json())
  ]);
  
  return { users, posts };
}
```

## 七、展开运算符

### 7.1 数组展开

```javascript
const arr1 = [1, 2, 3];
const arr2 = [...arr1, 4, 5];
// [1, 2, 3, 4, 5]

const merged = [...arr1, ...arr2];
```

### 7.2 对象展开

```javascript
const obj1 = { a: 1, b: 2 };
const obj2 = { ...obj1, c: 3 };
// { a: 1, b: 2, c: 3 }
```

## 八、类和模块

### 8.1 类

```javascript
class User {
  constructor(name) {
    this.name = name;
  }
  
  greet() {
    return `Hello, ${this.name}`;
  }
  
  static create(name) {
    return new User(name);
  }
}

class Admin extends User {
  constructor(name, role) {
    super(name);
    this.role = role;
  }
}
```

### 8.2 模块

```javascript
// export.js
export const name = '张三';
export function greet() { return 'Hi'; }
export default class User {}

// import.js
import User, { name, greet } from './export.js';
```

## 九、总结

ES6+ 核心要点：

1. **let/const**：块级作用域
2. **箭头函数**：简写和 this 绑定
3. **解构赋值**：快速提取
4. **模板字符串**：嵌入变量
5. **Promise**：异步编程
6. **async/await**：同步写法
7. **展开运算符**：合并数据
8. **类/模块**：面向对象和模块化

掌握这些，现代 JavaScript 不再难！

---

**推荐阅读**：
- [MDN JavaScript 指南](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)

**如果对你有帮助，欢迎点赞收藏！**
