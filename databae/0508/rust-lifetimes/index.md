# Rust 生命周期完全指南

## 一、生命周期基础

```rust
// 显式生命周期注解
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

fn main() {
    let s1 = String::from("hello");
    let s2 = String::from("world");
    let result = longest(&s1, &s2);
    println!("{}", result);
}
```

## 二、结构体中的生命周期

```rust
// 结构体持有引用需要生命周期
struct ImportantExcerpt<'a> {
    part: &'a str,
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().unwrap();
    let excerpt = ImportantExcerpt { part: first_sentence };
}
```

## 三、生命周期省略规则

```rust
// 规则 1：每个引用参数都有自己的生命周期参数
// 规则 2：如果只有一个输入生命周期，那个生命周期被赋予所有输出生命周期
// 规则 3：如果有多个输入生命周期，但其中一个是 &self 或 &mut self，
//         self 的生命周期被赋予所有输出生命周期

// 编译器会自动推断
fn first_word(s: &str) -> &str {
    // ...
}
```

## 四、生命周期与 trait

```rust
use std::fmt::Display;

fn longest_with_an_announcement<'a, T>(
    x: &'a str,
    y: &'a str,
    ann: T,
) -> &'a str
where
    T: Display,
{
    println!("Announcement! {}", ann);
    if x.len() > y.len() { x } else { y }
}
```

## 五、生命周期与闭包

```rust
fn main() {
    let x = 5;
    let closure = || println!("x: {}", x); // 借用 x
    closure();
}
```

## 六、最佳实践

- 让编译器尽可能自动推断生命周期
- 理解生命周期省略规则
- 使用 'static 生命周期（字符串字面量）
- 生命周期与所有权配合
- 避免不必要的复杂生命周期约束
- 阅读和理解编译错误信息
