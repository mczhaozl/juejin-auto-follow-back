# JavaScript + WebAssembly 性能优化完全指南

## 一、WebAssembly 概述

### 1.1 什么是 WebAssembly

低级汇编语言，可在浏览器中以接近原生性能运行。

### 1.2 优点

- 高性能
- 与 JavaScript 互操作
- 小体积
- 安全

---

## 二、创建 WASM 模块

### 2.1 使用 Rust

```bash
# 安装工具
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli
```

```rust
// src/lib.rs
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[wasm_bindgen]
pub fn fib(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fib(n - 1) + fib(n - 2)
    }
}
```

```toml
# Cargo.toml
[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
```

```bash
cargo build --target wasm32-unknown-unknown --release
wasm-bindgen --out-dir ./pkg --target web ./target/wasm32-unknown-unknown/release/mywasm.wasm
```

---

## 三、在 JavaScript 中使用

```javascript
import init, { add, fib } from './pkg/mywasm.js';

async function run() {
  await init();
  
  console.log('1 + 2 =', add(1, 2));
  console.log('fib(40) =', fib(40));
}

run();
```

---

## 四、性能对比

```javascript
// JavaScript 版本
function fibJS(n) {
  if (n === 0) return 0;
  if (n === 1) return 1;
  return fibJS(n - 1) + fibJS(n - 2);
}

console.time('JS');
fibJS(40);
console.timeEnd('JS');  // 较慢

console.time('WASM');
fib(40);
console.timeEnd('WASM');  // 显著更快
```

---

## 五、内存共享

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn compute(data: &[f64]) -> Vec<f64> {
    data.iter().map(|&x| x * 2.0).collect()
}
```

```javascript
const input = new Float64Array([1, 2, 3, 4]);
const result = compute(input);
console.log(result);
```

---

## 六、图像处理示例

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn grayscale(data: &mut [u8]) {
    for i in (0..data.len()).step_by(4) {
        let r = data[i] as f32;
        let g = data[i + 1] as f32;
        let b = data[i + 2] as f32;
        let gray = (r * 0.299 + g * 0.587 + b * 0.114) as u8;
        data[i] = gray;
        data[i + 1] = gray;
        data[i + 2] = gray;
    }
}
```

```javascript
import init, { grayscale } from './pkg/image.js';

async function processImage() {
  await init();
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = new Uint8Array(imageData.data.buffer);
  grayscale(data);
  ctx.putImageData(imageData, 0, 0);
}
```

---

## 七、最佳实践

- 只把计算密集型部分移到 WASM
- 减少 JS/WASM 通信开销
- 使用 SIMD 优化
- 合理设计内存布局

---

## 总结

WebAssembly 为 JavaScript 提供了强大的性能补充，适合处理计算密集型任务。
