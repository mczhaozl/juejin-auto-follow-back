# Rust & WebAssembly 完全指南

## 一、项目初始化

```bash
cargo install wasm-pack
cargo new --lib my-wasm
cd my-wasm
```

```toml
# Cargo.toml
[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
```

## 二、简单函数

```rust
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

## 三、构建和使用

```bash
wasm-pack build --target web
```

```html
<!DOCTYPE html>
<html>
  <body>
    <script type="module">
      import init, { add, greet } from './pkg/my_wasm.js';
      
      async function run() {
        await init();
        console.log(add(1, 2));
        console.log(greet("World"));
      }
      run();
    </script>
  </body>
</html>
```

## 四、JS 交互

```rust
use wasm_bindgen::prelude::*;
use web_sys::console;

#[wasm_bindgen(start)]
pub fn start() {
    console::log_1(&"Wasm module loaded!".into());
}

#[wasm_bindgen]
pub fn log_to_console(s: &str) {
    console::log_1(&s.into());
}
```

## 五、最佳实践

- 合理的 API 设计
- 最小化 JS 交互
- 性能优化
- 内存管理
- 类型安全
- 测试和调试
