# Rust 入门完全指南：从零基础到实战项目

Rust 是一门系统编程语言，以内存安全、高性能和零成本抽象著称。本文将带你从零开始学习 Rust。

## 一、Rust 基础

### 1. 安装 Rust

```bash
# 使用 rustup 安装
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 验证安装
rustc --version
cargo --version
```

### 2. Hello World

```rust
// main.rs
fn main() {
    println!("Hello, World!");
}
```

```bash
# 编译并运行
rustc main.rs
./main

# 或者使用 Cargo
cargo new hello_world
cd hello_world
cargo run
```

### 3. 变量与可变性

```rust
fn main() {
    // 不可变变量（默认）
    let x = 5;
    println!("x = {}", x);
    // x = 6; // 错误！
    
    // 可变变量
    let mut y = 5;
    println!("y = {}", y);
    y = 6;
    println!("y = {}", y);
    
    // 变量遮蔽
    let z = 5;
    let z = z + 1;
    let z = z * 2;
    println!("z = {}", z); // 12
}
```

### 4. 数据类型

```rust
fn main() {
    // 标量类型
    let integer: i32 = 42;
    let float: f64 = 3.14;
    let boolean: bool = true;
    let character: char = 'A';
    
    // 复合类型
    let tuple: (i32, f64, char) = (500, 6.4, '😀');
    let (x, y, z) = tuple;
    println!("x = {}, y = {}, z = {}", x, y, z);
    println!("tuple.0 = {}", tuple.0);
    
    let array: [i32; 5] = [1, 2, 3, 4, 5];
    println!("array[0] = {}", array[0]);
    
    let zeros = [0; 5]; // [0, 0, 0, 0, 0]
}
```

### 5. 函数

```rust
fn main() {
    println!("5 + 3 = {}", add(5, 3));
    print_labeled_measurement(5, 'h');
}

fn add(x: i32, y: i32) -> i32 {
    x + y // 注意：没有分号，这是表达式
}

fn print_labeled_measurement(value: i32, unit_label: char) {
    println!("The measurement is: {}{}", value, unit_label);
}

// 语句与表达式
fn statements_and_expressions() {
    let y = {
        let x = 3;
        x + 1
    };
    println!("y = {}", y); // 4
}
```

### 6. 控制流

```rust
fn main() {
    // if 表达式
    let number = 7;
    if number < 5 {
        println!("condition was true");
    } else {
        println!("condition was false");
    }
    
    // if let
    let number = Some(7);
    if let Some(i) = number {
        println!("Matched: {}", i);
    }
    
    // loop
    let mut count = 0;
    'counting_up: loop {
        println!("count = {}", count);
        
        let mut remaining = 10;
        loop {
            println!("remaining = {}", remaining);
            if remaining == 9 {
                break;
            }
            if count == 2 {
                break 'counting_up;
            }
            remaining -= 1;
        }
        
        count += 1;
    }
    
    // while
    let mut number = 3;
    while number != 0 {
        println!("{}!", number);
        number -= 1;
    }
    
    // for
    let a = [10, 20, 30, 40, 50];
    for element in a {
        println!("the value is: {}", element);
    }
    
    for number in 1..4 {
        println!("{}!", number);
    }
    
    // match
    let number = 5;
    match number {
        1 => println!("One"),
        2 | 3 | 5 | 7 => println!("Prime"),
        6..=10 => println!("Between 6 and 10"),
        _ => println!("Something else"),
    }
}
```

## 二、所有权

### 1. 所有权规则

```rust
fn main() {
    // String 在堆上分配
    let s1 = String::from("hello");
    let s2 = s1; // s1 移动到 s2
    // println!("{}", s1); // 错误！s1 不再有效
    
    // 克隆（深拷贝）
    let s3 = String::from("hello");
    let s4 = s3.clone();
    println!("s3 = {}, s4 = {}", s3, s4);
    
    // 栈上的数据：Copy trait
    let x = 5;
    let y = x;
    println!("x = {}, y = {}", x, y); // 没问题
}
```

### 2. 引用与借用

```rust
fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1);
    println!("The length of '{}' is {}.", s1, len);
    
    // 可变引用
    let mut s = String::from("hello");
    change(&mut s);
    println!("{}", s);
    
    // 同一时间只能有一个可变引用
    let mut s = String::from("hello");
    let r1 = &mut s;
    // let r2 = &mut s; // 错误！
    println!("{}", r1);
    
    // 不能同时有可变和不可变引用
    let mut s = String::from("hello");
    let r1 = &s;
    let r2 = &s;
    // let r3 = &mut s; // 错误！
    println!("{} and {}", r1, r2);
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

fn change(some_string: &mut String) {
    some_string.push_str(", world");
}
```

### 3. Slice

```rust
fn main() {
    let s = String::from("hello world");
    
    let hello = &s[0..5];
    let world = &s[6..11];
    let hello_easy = &s[..5];
    let world_easy = &s[6..];
    let whole = &s[..];
    
    println!("{} {} {} {} {}", hello, world, hello_easy, world_easy, whole);
    
    let word = first_word(&s);
    println!("first word: {}", word);
    
    let a = [1, 2, 3, 4, 5];
    let slice = &a[1..3];
    assert_eq!(slice, &[2, 3]);
}

fn first_word(s: &String) -> &str {
    let bytes = s.as_bytes();
    
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    
    &s[..]
}
```

## 三、结构体

### 1. 定义与实例化

```rust
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}

fn main() {
    let user1 = User {
        active: true,
        username: String::from("someusername123"),
        email: String::from("someone@example.com"),
        sign_in_count: 1,
    };
    
    let user2 = User {
        email: String::from("another@example.com"),
        ..user1 // 结构体更新语法
    };
    
    // 元组结构体
    struct Color(i32, i32, i32);
    struct Point(i32, i32, i32);
    
    let black = Color(0, 0, 0);
    let origin = Point(0, 0, 0);
    
    // 类单元结构体
    struct AlwaysEqual;
    let subject = AlwaysEqual;
}

fn build_user(email: String, username: String) -> User {
    User {
        active: true,
        username,
        email,
        sign_in_count: 1,
    }
}
```

### 2. 方法

```rust
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
    
    // 关联函数
    fn square(size: u32) -> Self {
        Self {
            width: size,
            height: size,
        }
    }
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };
    
    let rect2 = Rectangle {
        width: 10,
        height: 40,
    };
    
    println!("The area of the rectangle is {} square pixels.", rect1.area());
    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));
    
    let sq = Rectangle::square(3);
    println!("sq: {:?}", sq);
}
```

## 四、枚举

### 1. 定义枚举

```rust
enum IpAddrKind {
    V4,
    V6,
}

enum IpAddr {
    V4(u8, u8, u8, u8),
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
        println!("Message called!");
    }
}

fn main() {
    let four = IpAddrKind::V4;
    let six = IpAddrKind::V6;
    
    let home = IpAddr::V4(127, 0, 0, 1);
    let loopback = IpAddr::V6(String::from("::1"));
    
    let msg = Message::Write(String::from("hello"));
    msg.call();
    
    // Option 枚举
    let some_number = Some(5);
    let some_char = Some('e');
    let absent_number: Option<i32> = None;
}
```

### 2. Option

```rust
fn main() {
    let x: i8 = 5;
    let y: Option<i8> = Some(5);
    
    // let sum = x + y; // 错误！
    
    let sum = x + y.unwrap();
    println!("sum = {}", sum);
    
    let five = Some(5);
    let six = plus_one(five);
    let none = plus_one(None);
}

fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i + 1),
    }
}
```

## 五、集合

### 1. Vector

```rust
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
}
```

### 2. String

```rust
fn main() {
    let mut s = String::new();
    
    let data = "initial contents";
    let s = data.to_string();
    
    let s = String::from("initial contents");
    
    let mut s = String::from("foo");
    s.push_str("bar");
    s.push('!');
    
    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");
    let s3 = s1 + &s2;
    
    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");
    let s = format!("{}-{}-{}", s1, s2, s3);
}
```

### 3. HashMap

```rust
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);
    
    let team_name = String::from("Blue");
    let score = scores.get(&team_name).copied().unwrap_or(0);
    
    for (key, value) in &scores {
        println!("{}: {}", key, value);
    }
    
    scores.entry(String::from("Blue")).or_insert(50);
    scores.entry(String::from("Red")).or_insert(50);
    
    let text = "hello world wonderful world";
    let mut map = HashMap::new();
    
    for word in text.split_whitespace() {
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }
    
    println!("{:?}", map);
}
```

## 六、错误处理

### 1. panic!

```rust
fn main() {
    // panic!("crash and burn");
    
    let v = vec![1, 2, 3];
    // v[100]; // panic!
}
```

### 2. Result

```rust
use std::fs::File;
use std::io::Error;

fn main() {
    let greeting_file_result = File::open("hello.txt");
    
    let greeting_file = match greeting_file_result {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };
    
    let greeting_file = File::open("hello.txt").unwrap();
    let greeting_file = File::open("hello.txt")
        .expect("hello.txt should be included in this project");
}

fn read_username_from_file() -> Result<String, Error> {
    let username_file_result = File::open("hello.txt");
    
    let mut username_file = match username_file_result {
        Ok(file) => file,
        Err(e) => return Err(e),
    };
    
    let mut username = String::new();
    
    match username_file.read_to_string(&mut username) {
        Ok(_) => Ok(username),
        Err(e) => Err(e),
    }
}

fn read_username_from_file_short() -> Result<String, Error> {
    let mut username_file = File::open("hello.txt")?;
    let mut username = String::new();
    username_file.read_to_string(&mut username)?;
    Ok(username)
}
```

## 七、泛型

### 1. 函数泛型

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    
    largest
}

fn main() {
    let number_list = vec![34, 50, 25, 100, 65];
    let result = largest(&number_list);
    println!("The largest number is {}", result);
    
    let char_list = vec!['y', 'm', 'a', 'q'];
    let result = largest(&char_list);
    println!("The largest char is {}", result);
}
```

### 2. 结构体泛型

```rust
struct Point<T> {
    x: T,
    y: T,
}

struct Point2<T, U> {
    x: T,
    y: U,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

fn main() {
    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.0, y: 4.0 };
    let both_integer = Point2 { x: 5, y: 10 };
    let integer_and_float = Point2 { x: 5, y: 4.0 };
}
```

## 八、Trait

### 1. 定义 Trait

```rust
pub trait Summary {
    fn summarize(&self) -> String;
    
    fn summarize_default(&self) -> String {
        String::from("(Read more...)")
    }
}

pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

fn main() {
    let tweet = Tweet {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        retweet: false,
    };
    
    println!("1 new tweet: {}", tweet.summarize());
}
```

### 2. Trait 作为参数

```rust
pub fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}

pub fn notify2<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}

pub fn notify3(item: &(impl Summary + Display)) {}

pub fn notify4<T: Summary + Display>(item: &T) {}

fn some_function<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) -> i32 {}

fn some_function2<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug,
{}
```

## 九、实战项目：命令行工具

```rust
use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    let query = &args[1];
    let file_path = &args[2];
    
    println!("Searching for {}", query);
    println!("In file {}", file_path);
    
    let contents = fs::read_to_string(file_path)
        .expect("Should have been able to read the file");
    
    println!("With text:\n{}", contents);
}
```

## 十、总结

Rust 的核心特性：
- 所有权系统保证内存安全
- 零成本抽象
- 模式匹配
- Trait 系统
- 强大的错误处理
- 高性能

开始你的 Rust 之旅吧！
