# WebAssembly 入门指南：高性能 Web 开发

> 全面介绍 WebAssembly 技术，包括 Rust/C++ 编译为 WASM、在 JavaScript 中调用，以及实际性能优化案例。

## 一、WebAssembly 简介

### 1.1 什么是 WebAssembly

WebAssembly（WASM）是网页的新运行时：

- **高性能**：接近原生速度
- **可移植**：跨平台、跨语言
- **安全**：在沙箱中运行

### 1.2 对比 JavaScript

| JavaScript | WebAssembly |
|------------|-------------|
| 解释执行 | 编译执行 |
| 动态类型 | 静态类型 |
| 灵活 | 高性能 |

## 二、Hello World

### 2.1 Rust 示例

```rust
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

编译：

```bash
cargo build --target webassembly32-unknown-unknown
```

### 2.2 JavaScript 调用

```javascript
const wasm = await WebAssembly.instantiateStreaming(
  fetch('add.wasm')
);

const result = wasm.instance.exports.add(1, 2);
console.log(result); // 3
```

## 三、内存管理

### 3.1 线性内存

```javascript
const memory = new WebAssembly.Memory({ initial: 1, maximum: 10 });

// 在 WASM 中导出内存
// exports.memory
```

### 3.2 数据交换

```javascript
const view = new Int32Array(memory.buffer);

// WASM 写入数据
// memory.buffer[0] = 42;

// JavaScript 读取
console.log(view[0]);
```

## 四、Rust 实战

### 4.1 基础项目

```bash
cargo new --lib wasm-demo
```

配置 `Cargo.toml`：

```toml
[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
```

### 4.2 编写代码

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2)
    }
}
```

编译：

```bash
wasm-pack build --target web
```

## 五、JavaScript 集成

### 5.1 使用 wasm-pack

```javascript
import init, { fibonacci } from './pkg/wasm_demo.js';

await init();
console.log(fibonacci(20));
```

### 5.2 NPM 包

```bash
npm install wasm-demo
```

## 六、性能优化

### 6.1 何时使用 WASM

- 图像/视频处理
- 加密计算
- 游戏引擎
- 数据处理

### 6.2 性能对比

```javascript
// JavaScript
function fib(n) {
  if (n <= 1) return n;
  return fib(n - 1) + fib(n - 2);
}

// WASM - 更快
const result = fibonacci(40);
```

## 七、应用场景

### 7.1 图片处理

```rust
#[wasm_bindgen]
pub fn grayscale(data: &mut [u8]) {
    for i in (0..data.len()).step_by(4) {
        let gray = (data[i] as f32 * 0.299
            + data[i + 1] as f32 * 0.587
            + data[i + 2] as f32 * 0.114) as u8;
        data[i] = gray;
        data[i + 1] = gray;
        data[i + 2] = gray;
    }
}
```

### 7.2 游戏开发

```javascript
// 使用 Unity/Unreal 导出 WASM
import loadGame from './game.wasm';

const game = await loadGame({ canvas: '#game-canvas' });
game.start();
```

## 八、总结

WebAssembly 核心要点：

1. **高性能**：编译执行，接近原生
2. **多语言**：Rust、C++、Go 皆可
3. **内存**：线性内存共享
4. **集成**：与 JavaScript 互操作
5. **场景**：图像、游戏、计算密集型

掌握这些，Web 性能再升级！

---

**推荐阅读**：
- [MDN WebAssembly](https://developer.mozilla.org/en-US/docs/WebAssembly)
- [wasm-pack](https://rustwasm.github.io/wasm-pack/)

**如果对你有帮助，欢迎点赞收藏！**
