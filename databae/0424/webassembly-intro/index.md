# WebAssembly 完全入门指南：从基础到实战项目

WebAssembly (Wasm) 是一种新型的低级字节码格式，让我们可以在浏览器中运行接近原生速度的代码。本文将带你全面掌握 WebAssembly。

## 一、WebAssembly 基础

### 1. 什么是 WebAssembly

WebAssembly 是一种二进制指令格式，设计目标是：
- 接近原生的执行速度
- 紧凑的二进制格式
- 安全的沙箱执行环境
- 与 JavaScript 无缝集成

```
┌─────────────────────────────────────┐
│           浏览器                      │
│  ┌─────────────┐    ┌─────────────┐ │
│  │  JavaScript │    │ WebAssembly │ │
│  └─────────────┘    └─────────────┘ │
│         ↓                   ↓         │
│  ┌───────────────────────────────┐   │
│  │       引擎 (V8/SpiderMonkey)   │   │
│  └───────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 2. 第一个 WebAssembly 模块

使用 C 语言编写：

```c
// math.c
int add(int a, int b) {
  return a + b;
}

int multiply(int a, int b) {
  return a * b;
}
```

编译为 WebAssembly：

```bash
# 使用 Emscripten
emcc math.c -o math.wasm -s EXPORTED_FUNCTIONS='["_add", "_multiply"]'
```

在浏览器中使用：

```html
<!DOCTYPE html>
<html>
<body>
  <script>
    async function init() {
      // 加载 WebAssembly 模块
      const response = await fetch('math.wasm');
      const bytes = await response.arrayBuffer();
      const { instance } = await WebAssembly.instantiate(bytes);
      
      // 调用导出的函数
      const { add, multiply } = instance.exports;
      console.log(add(2, 3)); // 输出: 5
      console.log(multiply(4, 5)); // 输出: 20
    }
    
    init();
  </script>
</body>
</html>
```

### 3. 使用 Rust 编写 WebAssembly

```rust
// src/lib.rs
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
  a + b
}

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
  format!("Hello, {}!", name)
}
```

```toml
# Cargo.toml
[package]
name = "wasm-demo"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
```

```bash
# 编译
wasm-pack build --target web
```

使用：

```javascript
import init, { add, greet } from './pkg/wasm_demo.js';

async function run() {
  await init();
  
  console.log(add(2, 3)); // 输出: 5
  console.log(greet('World')); // 输出: "Hello, World!"
}

run();
```

## 二、核心概念

### 1. 模块（Module）

```javascript
// 加载模块
const module = await WebAssembly.compile(bytes);

// 或者直接实例化
const { module, instance } = await WebAssembly.instantiateStreaming(
  fetch('module.wasm')
);
```

### 2. 实例（Instance）

```javascript
// 实例化模块
const importObject = {
  env: {
    memory: new WebAssembly.Memory({ initial: 1 }),
    table: new WebAssembly.Table({ initial: 0, element: 'anyfunc' }),
    abort: (msg, file, line, column) => {
      console.error(`Abort: ${msg} at ${file}:${line}:${column}`);
    }
  }
};

const instance = await WebAssembly.instantiate(module, importObject);
```

### 3. 内存（Memory）

```javascript
// 创建内存
const memory = new WebAssembly.Memory({
  initial: 1, // 1 页 = 64KB
  maximum: 10 // 最多 10 页
});

// 写入内存
const array = new Uint8Array(memory.buffer);
array[0] = 42;
array[1] = 100;

// 读取内存
console.log(array[0]); // 输出: 42

// 增长内存
memory.grow(1); // 增加 1 页
```

### 4. 表格（Table）

```javascript
// 创建表格
const table = new WebAssembly.Table({
  initial: 2,
  element: 'anyfunc',
  maximum: 10
});

// 设置函数引用
function add(a, b) { return a + b; }
function multiply(a, b) { return a * b; }

table.set(0, add);
table.set(1, multiply);

// 调用表格中的函数
console.log(table.get(0)(2, 3)); // 输出: 5
console.log(table.get(1)(4, 5)); // 输出: 20
```

## 三、与 JavaScript 交互

### 1. 导出函数

```c
// wasm_module.c
#include <emscripten/emscripten.h>

EMSCRIPTEN_KEEPALIVE
int add(int a, int b) {
  return a + b;
}

EMSCRIPTEN_KEEPALIVE
float compute_pi(int iterations) {
  float pi = 0.0f;
  for (int i = 0; i < iterations; i++) {
    float sign = (i % 2 == 0) ? 1.0f : -1.0f;
    pi += sign / (2 * i + 1);
  }
  return 4 * pi;
}
```

```javascript
// 使用 Emscripten
const Module = require('./wasm_module.js');

Module.onRuntimeInitialized = function() {
  console.log(Module._add(2, 3));
  console.log(Module._compute_pi(1000000));
};
```

### 2. 导入函数

```c
// 声明要导入的函数
extern void log_message(const char* message);

EMSCRIPTEN_KEEPALIVE
void greet(const char* name) {
  char buffer[100];
  sprintf(buffer, "Hello, %s!", name);
  log_message(buffer);
}
```

```javascript
// JavaScript 端提供导入
const importObject = {
  env: {
    log_message: (ptr) => {
      const bytes = new Uint8Array(memory.buffer, ptr);
      let str = '';
      for (let i = 0; bytes[i] !== 0; i++) {
        str += String.fromCharCode(bytes[i]);
      }
      console.log(str);
    }
  }
};
```

### 3. 字符串处理

```rust
// Rust 示例
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn reverse_string(s: &str) -> String {
  s.chars().rev().collect()
}

#[wasm_bindgen]
pub fn count_vowels(s: &str) -> usize {
  s.chars()
    .filter(|&c| "aeiouAEIOU".contains(c))
    .count()
}
```

```javascript
// 使用
console.log(reverse_string("Hello")); // 输出: "olleH"
console.log(count_vowels("Hello World")); // 输出: 3
```

## 四、实战项目：图像处理

### 1. Rust 实现图像灰度化

```rust
// src/lib.rs
use wasm_bindgen::prelude::*;
use web_sys::ImageData;

#[wasm_bindgen]
pub fn grayscale(image_data: &ImageData) -> Vec<u8> {
  let data = image_data.data();
  let mut output = Vec::with_capacity(data.len());
  
  for i in (0..data.len()).step_by(4) {
    let r = data[i] as f32;
    let g = data[i + 1] as f32;
    let b = data[i + 2] as f32;
    let a = data[i + 3];
    
    // 加权灰度化
    let gray = (0.299 * r + 0.587 * g + 0.114 * b) as u8;
    
    output.push(gray);
    output.push(gray);
    output.push(gray);
    output.push(a);
  }
  
  output
}

#[wasm_bindgen]
pub fn blur(image_data: &ImageData, radius: usize) -> Vec<u8> {
  let width = image_data.width() as usize;
  let height = image_data.height() as usize;
  let data = image_data.data();
  let mut output = Vec::with_capacity(data.len());
  
  for y in 0..height {
    for x in 0..width {
      let mut sum_r = 0;
      let mut sum_g = 0;
      let mut sum_b = 0;
      let mut count = 0;
      
      for dy in -(radius as isize)..=(radius as isize) {
        for dx in -(radius as isize)..=(radius as isize) {
          let nx = x as isize + dx;
          let ny = y as isize + dy;
          
          if nx >= 0 && nx < width as isize && ny >= 0 && ny < height as isize {
            let idx = ((ny as usize * width + nx as usize) * 4) as usize;
            sum_r += data[idx] as u32;
            sum_g += data[idx + 1] as u32;
            sum_b += data[idx + 2] as u32;
            count += 1;
          }
        }
      }
      
      let idx = (y * width + x) * 4;
      output.push((sum_r / count) as u8);
      output.push((sum_g / count) as u8);
      output.push((sum_b / count) as u8);
      output.push(data[idx + 3]);
    }
  }
  
  output
}
```

### 2. JavaScript 集成

```html
<!DOCTYPE html>
<html>
<body>
  <input type="file" id="imageInput" accept="image/*">
  <canvas id="originalCanvas"></canvas>
  <canvas id="processedCanvas"></canvas>
  
  <script type="module">
    import init, { grayscale, blur } from './pkg/image_processor.js';
    
    const originalCanvas = document.getElementById('originalCanvas');
    const processedCanvas = document.getElementById('processedCanvas');
    const imageInput = document.getElementById('imageInput');
    
    let originalCtx, processedCtx;
    
    async function run() {
      await init();
      
      originalCtx = originalCanvas.getContext('2d');
      processedCtx = processedCanvas.getContext('2d');
    }
    
    imageInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      const reader = new FileReader();
      
      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
          originalCanvas.width = img.width;
          originalCanvas.height = img.height;
          processedCanvas.width = img.width;
          processedCanvas.height = img.height;
          
          originalCtx.drawImage(img, 0, 0);
          
          // 灰度化
          const imageData = originalCtx.getImageData(0, 0, img.width, img.height);
          const grayData = grayscale(imageData);
          const grayImageData = new ImageData(
            new Uint8ClampedArray(grayData),
            img.width,
            img.height
          );
          processedCtx.putImageData(grayImageData, 0, 0);
        };
        img.src = event.target.result;
      };
      reader.readAsDataURL(file);
    });
    
    run();
  </script>
</body>
</html>
```

## 五、性能优化

### 1. 减少 JavaScript ↔ WebAssembly 调用

```javascript
// ❌ 不好：频繁调用
for (let i = 0; i < 1000; i++) {
  wasmModule.doSomething(i);
}

// ✅ 好：批量处理
wasmModule.doManyThings(1000);
```

### 2. 合理使用内存

```javascript
// 预分配内存
const memory = new WebAssembly.Memory({ initial: 10 });
const data = new Float32Array(memory.buffer, 0, 1000000);
```

### 3. 使用 SIMD（单指令多数据）

```rust
// Rust 中使用 SIMD
use core::arch::wasm32::*;

#[wasm_bindgen]
pub fn simd_add(a: &[f32], b: &[f32]) -> Vec<f32> {
  let mut result = Vec::with_capacity(a.len());
  
  for i in (0..a.len()).step_by(4) {
    unsafe {
      let va = v128_load(a.as_ptr().add(i) as *const v128);
      let vb = v128_load(b.as_ptr().add(i) as *const v128);
      let vr = f32x4_add(va, vb);
      v128_store(result.as_mut_ptr().add(i) as *mut v128, vr);
    }
  }
  
  result.set_len(a.len());
  result
}
```

## 六、最佳实践

1. 选择合适的语言（Rust、C/C++、AssemblyScript）
2. 最小化 JavaScript ↔ WebAssembly 通信
3. 合理管理内存
4. 使用 SIMD 优化密集计算
5. 提供清晰的 API
6. 添加错误处理
7. 编写测试
8. 使用工具链优化

## 七、总结

WebAssembly 核心要点：
- 理解基本概念（模块、实例、内存、表格）
- 掌握与 JavaScript 的交互
- 使用 Rust 或 AssemblyScript 开发
- 实现性能密集型应用
- 优化通信和内存使用
- 遵循最佳实践

开始用 WebAssembly 加速你的 Web 应用吧！
