# Rust 模式匹配完全指南

## 一、基础 match

```rust
fn main() {
    let number = 7;
    
    match number {
        0 => println!("zero"),
        1 | 2 => println!("one or two"),
        3..=10 => println!("three to ten"),
        _ => println!("something else"),
    }
}
```

## 二、解构

```rust
// 元组解构
let pair = (0, -2);
match pair {
    (0, y) => println!("x is 0, y is {}", y),
    (x, 0) => println!("x is {}, y is 0", x),
    _ => println!("Neither is 0"),
}

// 结构体解构
struct Point { x: i32, y: i32 }

let p = Point { x: 0, y: 7 };
match p {
    Point { x, y: 0 } => println!("x is {}", x),
    Point { x: 0, y } => println!("y is {}", y),
    Point { x, y } => println!("({}, {})", x, y),
}
```

## 三、守卫

```rust
let pair = (2, -2);
match pair {
    (x, y) if x == y => println!("twins"),
    (x, y) if x + y == 0 => println!("opposites"),
    (x, y) if x + y > 0 => println!("positive sum"),
    _ => println!("others"),
}
```

## 四、Option 和 Result

```rust
fn divide(x: i32, y: i32) -> Option<i32> {
    if y == 0 { None } else { Some(x / y) }
}

match divide(4, 2) {
    Some(n) if n % 2 == 0 => println!("even"),
    Some(n) => println!("{}", n),
    None => println!("can't divide by zero"),
}
```

## 五、let-else

```rust
// 解构失败时返回
let Some(x) = foo() else {
    return;
};
```

## 六、最佳实践

- 使用穷尽性检查（match 必须覆盖所有情况）
- 使用 _ 通配符处理剩余情况
- 使用 if let 简化 Option/Result 处理
- 模式守卫提供额外条件
- 利用结构体和枚举解构
- 避免过于复杂的模式
