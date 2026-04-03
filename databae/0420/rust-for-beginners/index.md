# Rust 入门完全指南：从安装到实战

Rust 是一门系统编程语言，专注于安全性、速度和并发性。本文将带你从零开始学习 Rust。

## 一、Rust 简介

### 1. 什么是 Rust

Rust 是 Mozilla 开发的一门现代系统编程语言，专注于安全、并发和性能。

### 2. Rust 的特点

- **内存安全**：无需垃圾回收，编译时检查
- **零成本抽象**：高级特性不影响性能
- **并发安全**：Fearless Concurrency
- **高性能**：媲美 C/C++
- **现代工具链**：Cargo 包管理器
- **丰富生态**：crates.io 包仓库

### 3. 适用场景

- **系统编程**：操作系统、驱动程序
- **Web 开发**：后端服务、WASM
- **游戏开发**：游戏引擎、高性能游戏
- **嵌入式开发**：IoT 设备
- **工具链**：CLI 工具、库

## 二、安装 Rust

### 1. 使用 rustup 安装

```bash
# Linux/macOS
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Windows
# 下载：https://rustup.rs/
```

### 2. 验证安装

```bash
# 查看版本
rustc --version
cargo --version
rustup --version

# 更新 Rust
rustup update

# 查看文档
rustup doc
```

### 3. 常见工具

```bash
# rustup 管理工具链
rustup install stable
rustup install nightly
rustup default stable
rustup override set nightly

# 组件
rustup component add rust-src
rustup component add rust-analyzer
rustup component add clippy
rustup component add rustfmt
```

## 三、Hello World

### 1. 第一个程序

```rust
// main.rs
fn main() {
    println!("Hello, World!");
}
```

```bash
# 编译
rustc main.rs

# 运行
./main  # Linux/macOS
main.exe # Windows
```

### 2. 使用 Cargo

```bash
# 创建项目
cargo new hello_rust
cd hello_rust

# 目录结构
# hello_rust/
# ├── Cargo.toml
# └── src/
#     └── main.rs
```

```toml
# Cargo.toml
[package]
name = "hello_rust"
version = "0.1.0"
edition = "2021"

[dependencies]
```

```rust
// src/main.rs
fn main() {
    println!("Hello, Rust!");
}
```

```bash
# 运行
cargo run

# 构建
cargo build
cargo build --release  # 发布版本

# 检查
cargo check

# 测试
cargo test

# 格式化
cargo fmt

# Clippy 检查
cargo clippy
```

## 四、基础语法

### 1. 变量和可变性

```rust
fn main() {
    // 不可变变量
    let x = 5;
    println!("x = {}", x);

    // 可变变量
    let mut y = 5;
    println!("y = {}", y);
    y = 6;
    println!("y = {}", y);

    // 常量
    const MAX_POINTS: u32 = 100_000;
    println!("MAX_POINTS = {}", MAX_POINTS);

    // 遮蔽（Shadowing）
    let z = 5;
    let z = z + 1;
    let z = z * 2;
    println!("z = {}", z);
}
```

### 2. 数据类型

```rust
fn main() {
    // 标量类型
    let a: i32 = -42;
    let b: u32 = 42;
    let c: f64 = 3.14159;
    let d: bool = true;
    let e: char = '😀';

    // 整型
    let _i8: i8 = -128;
    let _i16: i16 = -32768;
    let _i32: i32 = -2147483648;
    let _i64: i64 = -9223372036854775808;
    let _i128: i128 = -170141183460469231731687303715884105728;

    let _u8: u8 = 255;
    let _u16: u16 = 65535;
    let _u32: u32 = 4294967295;
    let _u64: u64 = 18446744073709551615;
    let _u128: u128 = 340282366920938463463374607431768211455;

    let _isize: isize = -1;
    let _usize: usize = 1;

    // 数字字面量
    let _decimal = 98_222;
    let _hex = 0xff;
    let _octal = 0o77;
    let _binary = 0b1111_0000;
    let _byte = b'A';

    // 浮点
    let _x = 2.0; // f64
    let _y: f32 = 3.0; // f32

    // 布尔
    let _t = true;
    let _f: bool = false;

    // 字符
    let _c = 'z';
    let _z: char = 'ℤ';
    let _heart_eyed_cat = '😻';

    // 复合类型
    let tup: (i32, f64, char) = (500, 6.4, '1');
    let (x, y, z) = tup;
    let five_hundred = tup.0;
    let six_point_four = tup.1;
    let one = tup.2;

    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    let first = arr[0];
    let second = arr[1];
    let _a = [3; 5]; // [3, 3, 3, 3, 3]
}
```

### 3. 函数

```rust
fn main() {
    println!("Hello, world!");
    another_function();
    another_function2(5);
    print_labeled_measurement(5, 'h');

    let y = {
        let x = 3;
        x + 1
    };
    println!("y = {}", y);

    let x = five();
    println!("x = {}", x);

    let x = plus_one(5);
    println!("x = {}", x);
}

fn another_function() {
    println!("Another function.");
}

fn another_function2(x: i32) {
    println!("x = {}", x);
}

fn print_labeled_measurement(value: i32, unit_label: char) {
    println!("The measurement is: {}{}", value, unit_label);
}

fn five() -> i32 {
    5
}

fn plus_one(x: i32) -> i32 {
    x + 1
}
```

### 4. 控制流

```rust
fn main() {
    let number = 3;

    if number < 5 {
        println!("condition was true");
    } else {
        println!("condition was false");
    }

    let number = 6;
    if number % 4 == 0 {
        println!("number is divisible by 4");
    } else if number % 3 == 0 {
        println!("number is divisible by 3");
    } else if number % 2 == 0 {
        println!("number is divisible by 2");
    } else {
        println!("number is not divisible by 4, 3, or 2");
    }

    let condition = true;
    let number = if condition { 5 } else { 6 };
    println!("number = {}", number);

    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter * 2;
        }
    };
    println!("result = {}", result);

    let mut number = 3;
    while number != 0 {
        println!("{}!", number);
        number -= 1;
    }
    println!("LIFTOFF!!!");

    let a = [10, 20, 30, 40, 50];
    for element in a {
        println!("the value is: {}", element);
    }

    for number in (1..4).rev() {
        println!("{}!", number);
    }
    println!("LIFTOFF!!!");
}
```

## 五、所有权（Ownership）

### 1. 所有权规则

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;
    // println!("{}, world!", s1); // 错误！s1 已经无效
    println!("{}, world!", s2);

    let s1 = String::from("hello");
    let s2 = s1.clone();
    println!("s1 = {}, s2 = {}", s1, s2);

    let x = 5;
    let y = x;
    println!("x = {}, y = {}", x, y);

    let s = String::from("hello");
    takes_ownership(s);
    // println!("{}", s); // 错误！

    let x = 5;
    makes_copy(x);
    println!("{}", x); // 没问题

    let s1 = gives_ownership();
    let s2 = String::from("hello");
    let s3 = takes_and_gives_back(s2);

    let s1 = String::from("hello");
    let (s2, len) = calculate_length(s1);
    println!("The length of '{}' is {}.", s2, len);
}

fn takes_ownership(some_string: String) {
    println!("{}", some_string);
}

fn makes_copy(some_integer: i32) {
    println!("{}", some_integer);
}

fn gives_ownership() -> String {
    let some_string = String::from("yours");
    some_string
}

fn takes_and_gives_back(a_string: String) -> String {
    a_string
}

fn calculate_length(s: String) -> (String, usize) {
    let length = s.len();
    (s, length)
}
```

### 2. 引用和借用

```rust
fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1);
    println!("The length of '{}' is {}.", s1, len);

    let mut s = String::from("hello");
    change(&mut s);
    println!("{}", s);

    let mut s = String::from("hello");
    let r1 = &mut s;
    // let r2 = &mut s; // 错误！不能同时有两个可变引用
    println!("{}", r1);

    let mut s = String::from("hello");
    let r1 = &s;
    let r2 = &s;
    // let r3 = &mut s; // 错误！不能同时有不可变和可变引用
    println!("{} and {}", r1, r2);

    let mut s = String::from("hello");
    let r1 = &s;
    let r2 = &s;
    println!("{} and {}", r1, r2);
    let r3 = &mut s; // 没问题，r1 和 r2 不再使用
    println!("{}", r3);

    let reference_to_nothing = dangle();
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

fn change(some_string: &mut String) {
    some_string.push_str(", world");
}

fn dangle() -> &String {
    let s = String::from("hello");
    &s // 错误！返回悬垂引用
}
```

### 3. 切片

```rust
fn main() {
    let mut s = String::from("hello world");
    let word = first_word(&s);
    // s.clear(); // 错误！不能同时有可变和不可变引用
    println!("the first word is: {}", word);

    let a = [1, 2, 3, 4, 5];
    let slice = &a[1..3];
    assert_eq!(slice, &[2, 3]);
}

fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}
```

## 六、结构体

```rust
fn main() {
    let user1 = User {
        active: true,
        username: String::from("someusername123"),
        email: String::from("someone@example.com"),
        sign_in_count: 1,
    };

    let user2 = User {
        email: String::from("another@example.com"),
        ..user1
    };

    let black = Color(0, 0, 0);
    let origin = Point(0, 0, 0);

    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };
    println!("rect1 is {:?}", rect1);
    println!("The area of the rectangle is {} square pixels.", area(&rect1));
    println!("The area of the rectangle is {} square pixels.", rect1.area());

    let rect2 = Rectangle {
        width: 10,
        height: 40,
    };
    let rect3 = Rectangle {
        width: 60,
        height: 45,
    };
    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));
    println!("Can rect1 hold rect3? {}", rect1.can_hold(&rect3));

    let sq = Rectangle::square(3);
    println!("square is {:?}", sq);
}

#[derive(Debug)]
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}

struct Color(i32, i32, i32);
struct Point(i32, i32, i32);

#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }

    fn square(size: u32) -> Self {
        Self {
            width: size,
            height: size,
        }
    }
}

fn area(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}
```

## 七、枚举和模式匹配

```rust
fn main() {
    let four = IpAddrKind::V4;
    let six = IpAddrKind::V6;

    let home = IpAddr::V4(String::from("127.0.0.1"));
    let loopback = IpAddr::V6(String::from("::1"));

    let m = Message::Write(String::from("hello"));
    m.call();

    let some_number = Some(5);
    let some_char = Some('e');
    let absent_number: Option<i32> = None;

    let x: i8 = 5;
    let y: Option<i8> = Some(5);
    let sum = x + y.unwrap_or(0);

    let coin = Coin::Penny;
    let value = value_in_cents(coin);
    println!("value is {}", value);

    let five = Some(5);
    let six = plus_one(five);
    let none = plus_one(None);

    let some_u8_value = Some(0u8);
    if let Some(3) = some_u8_value {
        println!("three");
    }
}

enum IpAddrKind {
    V4,
    V6,
}

enum IpAddr {
    V4(String),
    V6(String),
}

enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

impl Message {
    fn call(&self) {
        println!("call");
    }
}

#[derive(Debug)]
enum UsState {
    Alabama,
    Alaska,
}

enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(UsState),
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(state) => {
            println!("State quarter from {:?}!", state);
            25
        }
    }
}

fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i + 1),
    }
}
```

## 八、集合

```rust
use std::collections::{HashMap, HashSet};

fn main() {
    let v: Vec<i32> = Vec::new();
    let v = vec![1, 2, 3];

    let mut v = Vec::new();
    v.push(5);
    v.push(6);
    v.push(7);
    v.push(8);

    let third: &i32 = &v[2];
    println!("The third element is {}", third);

    let third: Option<&i32> = v.get(2);
    match third {
        Some(third) => println!("The third element is {}", third),
        None => println!("There is no third element."),
    }

    let v = vec![100, 32, 57];
    for i in &v {
        println!("{}", i);
    }

    let mut v = vec![100, 32, 57];
    for i in &mut v {
        *i += 50;
    }

    enum SpreadsheetCell {
        Int(i32),
        Float(f64),
        Text(String),
    }
    let row = vec![
        SpreadsheetCell::Int(3),
        SpreadsheetCell::Text(String::from("blue")),
        SpreadsheetCell::Float(10.12),
    ];

    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");
    let s = format!("{}-{}-{}", s1, s2, s3);

    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    let team_name = String::from("Blue");
    let score = scores.get(&team_name).copied().unwrap_or(0);

    for (key, value) in &scores {
        println!("{}: {}", key, value);
    }

    scores.insert(String::from("Blue"), 25);
    scores.entry(String::from("Blue")).or_insert(50);

    let text = "hello world wonderful world";
    let mut map = HashMap::new();
    for word in text.split_whitespace() {
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }
    println!("{:?}", map);

    let mut set: HashSet<i32> = HashSet::new();
    set.insert(1);
    set.insert(2);
    set.insert(3);
    set.insert(2);
    println!("set: {:?}", set);
}
```

## 九、错误处理

```rust
use std::fs::File;
use std::io::{self, Read};

fn main() {
    let f = File::open("hello.txt");
    let f = match f {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    let f = File::open("hello.txt").unwrap();
    let f = File::open("hello.txt").expect("Failed to open hello.txt");

    let result = read_username_from_file();
    let result = read_username_from_file2();
    let result = read_username_from_file3();
}

fn read_username_from_file() -> Result<String, io::Error> {
    let f = File::open("hello.txt");
    let mut f = match f {
        Ok(file) => file,
        Err(e) => return Err(e),
    };
    let mut s = String::new();
    match f.read_to_string(&mut s) {
        Ok(_) => Ok(s),
        Err(e) => Err(e),
    }
}

fn read_username_from_file2() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

fn read_username_from_file3() -> Result<String, io::Error> {
    let mut s = String::new();
    File::open("hello.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
```

## 十、泛型、Trait 和生命周期

```rust
fn main() {
    let number_list = vec![34, 50, 25, 100, 65];
    let result = largest(&number_list);
    println!("The largest number is {}", result);

    let char_list = vec!['y', 'm', 'a', 'q'];
    let result = largest(&char_list);
    println!("The largest char is {}", result);

    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.0, y: 4.0 };
    let p = Point { x: 5, y: 10.4 };

    let p1 = Point { x: 5, y: 10.4 };
    let p2 = Point { x: "Hello", y: 'c' };
    let p3 = p1.mixup(p2);

    let tweet = Tweet {
        username: String::from("horse_ebooks"),
        content: String::from("of course, as you probably already know, people"),
        reply: false,
        retweet: false,
    };
    println!("1 new tweet: {}", tweet.summarize());

    let article = NewsArticle {
        headline: String::from("Penguins win the Stanley Cup Championship!"),
        location: String::from("Pittsburgh, PA, USA"),
        author: String::from("Iceburgh"),
        content: String::from("The Pittsburgh Penguins once again are the best hockey team in the NHL."),
    };
    notify(&article);

    let string1 = String::from("abcd");
    let string2 = "xyz";
    let result = longest(string1.as_str(), string2);
    println!("The longest string is {}", result);

    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let i = ImportantExcerpt {
        part: first_sentence,
    };
}

fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

struct Point<T, U> {
    x: T,
    y: U,
}

impl<T, U> Point<T, U> {
    fn mixup<V, W>(self, other: Point<V, W>) -> Point<T, W> {
        Point {
            x: self.x,
            y: other.y,
        }
    }
}

pub trait Summary {
    fn summarize_author(&self) -> String;
    fn summarize(&self) -> String {
        format!("(Read more from {}...)", self.summarize_author())
    }
}

pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {
    fn summarize_author(&self) -> String {
        format!("@{}", self.author)
    }
}

pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}

impl Summary for Tweet {
    fn summarize_author(&self) -> String {
        format!("@{}", self.username)
    }
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

pub fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}

fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

struct ImportantExcerpt<'a> {
    part: &'a str,
}
```

## 十一、Cargo 和 Crates.io

```toml
# Cargo.toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <your@email.com>"]
description = "A project"
license = "MIT"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
rand = "0.8"
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
assert_cmd = "2.0"

[build-dependencies]
cc = "1.0"

[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
```

```bash
# 搜索 crate
cargo search serde

# 添加依赖
cargo add serde
cargo add serde --features derive

# 运行
cargo run
cargo run --release

# 测试
cargo test
cargo test -- --nocapture

# 文档
cargo doc --open

# 发布
cargo login
cargo publish

# 清理
cargo clean
```

## 十二、实战项目：命令行工具

```rust
use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: minigrep <query> <file>");
        std::process::exit(1);
    }

    let query = &args[1];
    let file_path = &args[2];

    let contents = fs::read_to_string(file_path)
        .expect("Should have been able to read the file");

    for line in search(query, &contents) {
        println!("{}", line);
    }
}

pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents
        .lines()
        .filter(|line| line.contains(query))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_result() {
        let query = "duct";
        let contents = "\
Rust:
safe, fast, productive.
Pick three.";
        assert_eq!(vec!["safe, fast, productive."], search(query, contents));
    }
}
```

## 十三、总结

Rust 是一门安全、高效、现代的系统编程语言。通过本文的学习，你应该已经掌握了：

1. Rust 的安装和工具链
2. 基础语法和数据类型
3. 所有权和借用系统
4. 结构体和枚举
5. 模式匹配
6. 错误处理
7. 泛型和 Trait
8. Cargo 的使用

继续深入学习 Rust，开启系统编程的新篇章！

## 参考资料

- [Rust 官方文档](https://doc.rust-lang.org/)
- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [crates.io](https://crates.io/)
