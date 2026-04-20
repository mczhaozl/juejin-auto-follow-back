# Rust 所有权与借用完全指南：从基础到实战

## 一、所有权基础

### 1.1 什么是所有权
所有权是 Rust 最核心的特性，无需垃圾回收即可保证内存安全。

### 1.2 所有权规则
1. 每个值都有一个所有者（Owner）
2. 同时只能有一个所有者
3. 所有者离开作用域时，值被自动释放

---

## 二、变量作用域

```rust
fn main() {
    // s 在这里无效
    let s = "hello"; // s 从这里开始有效
    println!("{}", s);
} // 作用域结束，s 不再有效
```

---

## 三、String 类型

String 类型在堆上分配内存，其内存管理由所有权控制。

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1; // s1 的所有权移动给 s2
    
    // println!("{}", s1); // 错误！s1 已不再有效
    println!("{}", s2); // 正确
}
```

---

## 四、克隆（Clone）

如果需要深拷贝堆上的数据，使用 clone：

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1.clone();
    
    println!("s1 = {}, s2 = {}", s1, s2); // 两者都有效
}
```

---

## 五、栈上数据：Copy

对于栈上完全存储的类型，Rust 默认会 Copy：

```rust
fn main() {
    let x = 5;
    let y = x; // Copy，不是 Move
    
    println!("x = {}, y = {}", x, y); // 两者都有效
}
```

Copy trait 的类型包括：
- 所有整数类型
- 布尔类型 bool
- 浮点数类型
- 字符类型 char
- 元组（Tuple），若其所有字段都是 Copy 的

---

## 六、所有权与函数

```rust
fn takes_ownership(s: String) {
    println!("{}", s);
} // s 离开作用域，内存释放

fn gives_ownership() -> String {
    let s = String::from("yours");
    s
}

fn takes_and_gives_back(s: String) -> String {
    s
}

fn main() {
    let s1 = gives_ownership();
    let s2 = String::from("hello");
    let s3 = takes_and_gives_back(s2);
}
```

---

## 七、引用与借用

### 7.1 引用基础

引用允许使用值但不取得所有权，称为借用（Borrowing）：

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}

fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1);
    println!("The length of '{}' is {}.", s1, len);
}
```

### 7.2 可变引用

```rust
fn change(some_string: &mut String) {
    some_string.push_str(", world");
}

fn main() {
    let mut s = String::from("hello");
    change(&mut s);
    println!("{}", s);
}
```

### 7.3 可变引用的限制

在特定作用域内，同一数据只能有一个可变引用：

```rust
fn main() {
    let mut s = String::from("hello");
    
    let r1 = &mut s;
    // let r2 = &mut s; // 错误！不能同时有两个可变引用
    
    println!("{}", r1);
}
```

同样，不能在有不可变引用时同时有可变引用：

```rust
fn main() {
    let mut s = String::from("hello");
    
    let r1 = &s;
    let r2 = &s;
    // let r3 = &mut s; // 错误！
    
    println!("{} and {}", r1, r2);
}
```

---

## 八、悬垂引用

```rust
fn dangle() -> &String {
    let s = String::from("hello");
    &s
} // s 离开作用域被释放，引用无效

fn main() {
    let reference_to_nothing = dangle();
}
```

---

## 九、切片（Slice）

字符串切片：

```rust
fn first_word(s: &String) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}

fn main() {
    let s = String::from("hello world");
    let word = first_word(&s);
    println!("The first word is: {}", word);
}
```

数组切片：

```rust
fn main() {
    let a = [1, 2, 3, 4, 5];
    let slice = &a[1..3];
    assert_eq!(slice, &[2, 3]);
}
```

---

## 十、生命周期（Lifetimes）

### 10.1 为什么需要生命周期

```rust
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() { x } else { y }
}
```

### 10.2 生命周期标注

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

### 10.3 结构体中的生命周期

```rust
struct ImportantExcerpt<'a> {
    part: &'a str,
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find");
    let i = ImportantExcerpt { part: first_sentence };
}
```

---

## 十一、生命周期省略规则

### 规则一
每个引用参数都有自己的生命周期参数。

### 规则二
如果只有一个输入生命周期，该生命周期被赋予所有输出生命周期。

### 规则三
如果有多个输入生命周期，但其中有一个是 &self 或 &mut self，那么 self 的生命周期被赋予所有输出生命周期。

---

## 十二、实战示例

### 12.1 用户管理系统

```rust
struct User<'a> {
    name: &'a str,
    email: &'a str,
}

impl<'a> User<'a> {
    fn new(name: &'a str, email: &'a str) -> Self {
        User { name, email }
    }
    
    fn greet(&self) {
        println!("Hello, I'm {}!", self.name);
    }
}

fn main() {
    let name = String::from("Alice");
    let email = String::from("alice@example.com");
    
    let user = User::new(&name, &email);
    user.greet();
}
```

### 12.2 字符串处理函数

```rust
fn trim_and_lowercase<'a>(s: &'a str) -> String {
    s.trim().to_lowercase()
}

fn concat_with_separator<'a>(s1: &'a str, s2: &'a str, separator: &str) -> String {
    format!("{}{}{}", s1, separator, s2)
}

fn main() {
    let s1 = "  Hello, WORLD!  ";
    let s2 = "  Rust  ";
    println!("{}", trim_and_lowercase(s1));
    println!("{}", concat_with_separator("hello", "world", " "));
}
```

---

## 十三、所有权最佳实践

1. 使用引用避免所有权转移
2. 优先使用不可变引用，需要时再可变
3. 遵循可变引用的单一性规则
4. 使用生命周期保证引用安全
5. 使用切片而非引用完整的 String

---

## 十四、总结

所有权、借用和生命周期是 Rust 的三大核心特性，掌握这些是学习 Rust 的关键。
