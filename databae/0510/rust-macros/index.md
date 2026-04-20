# Rust 宏完全指南

## 一、声明宏（Macro Rules）

```rust
// 简单宏
macro_rules! vec {
    ($($x:expr),*) => ({
        let mut temp_vec = Vec::new();
        $(temp_vec.push($x);)*
        temp_vec
    });
}

// 使用
let v = vec![1, 2, 3];
```

## 二、宏语法

```rust
macro_rules! foo {
    (x => $e:expr) => ($e);
    (y => $e:expr) => (2 * $e);
}

// 使用
assert_eq!(foo!(x => 42), 42);
assert_eq!(foo!(y => 42), 84);
```

## 三、过程宏

```rust
// 需要在单独的 proc-macro crate
use proc_macro::TokenStream;

#[proc_macro_derive(HelloWorld)]
pub fn hello_world_derive(input: TokenStream) -> TokenStream {
    // 实现
    input
}
```

## 四、属性宏

```rust
#[proc_macro_attribute]
pub fn log(_args: TokenStream, input: TokenStream) -> TokenStream {
    // 修改输入
    input
}
```

## 五、最佳实践

- 宏是强大但复杂的工具，谨慎使用
- 使用宏文档说明用法
- 使用 cargo-expand 调试宏
- 注意宏卫生（hygiene）
- 使用 syn 和 quote 编写过程宏
