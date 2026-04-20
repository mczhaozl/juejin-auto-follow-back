# Rust 错误处理完全指南：从 panic 到自定义错误

## 一、Rust 错误处理概述

Rust 将错误分为两类：
- **不可恢复错误**：panic!
- **可恢复错误**：Result&lt;T, E&gt;

---

## 二、panic! 宏

```rust
fn main() {
    panic!("crash and burn");
}

// 带 panic backtrace
// RUST_BACKTRACE=1 cargo run
```

---

## 三、Result 枚举

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}

use std::fs::File;

fn main() {
    let f = File::open("hello.txt");
    
    let f = match f {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };
}
```

---

## 四、unwrap 和 expect

```rust
use std::fs::File;

fn main() {
    // unwrap: 如果 Err 则 panic
    let f = File::open("hello.txt").unwrap();
    
    // expect: 自定义 panic 信息
    let f = File::open("hello.txt")
        .expect("Failed to open hello.txt");
}
```

---

## 五、传播错误

```rust
use std::fs::File;
use std::io;
use std::io::Read;

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
```

---

## 六、? 运算符

```rust
use std::fs::File;
use std::io;
use std::io::Read;

fn read_username_from_file() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

// 更简洁
fn read_username_from_file() -> Result<String, io::Error> {
    let mut s = String::new();
    File::open("hello.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
```

---

## 七、自定义错误类型

```rust
use std::fs::File;
use std::io;

#[derive(Debug)]
enum MyError {
    Io(io::Error),
    Parse(std::num::ParseIntError),
}

// 实现 Display
impl std::fmt::Display for MyError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            MyError::Io(e) => write!(f, "IO error: {}", e),
            MyError::Parse(e) => write!(f, "Parse error: {}", e),
        }
    }
}

// 实现 Error trait
impl std::error::Error for MyError {}

// From trait 自动转换
impl From<io::Error> for MyError {
    fn from(err: io::Error) -> MyError {
        MyError::Io(err)
    }
}

impl From<std::num::ParseIntError> for MyError {
    fn from(err: std::num::ParseIntError) -> MyError {
        MyError::Parse(err)
    }
}

// 使用
fn main() -> Result<(), MyError> {
    let f = File::open("hello.txt")?; // 自动转换为 MyError
    Ok(())
}
```

---

## 八、thiserror 库

```toml
[dependencies]
thiserror = "1.0"
```

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum MyError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Parse error: {0}")]
    Parse(#[from] std::num::ParseIntError),
    
    #[error("Custom error: {0}")]
    Custom(String),
}

fn main() -> Result<(), MyError> {
    use std::fs::File;
    let f = File::open("hello.txt")?;
    Ok(())
}
```

---

## 九、anyhow 库

```toml
[dependencies]
anyhow = "1.0"
```

```rust
use anyhow::{Context, Result};
use std::fs::File;
use std::io::Read;

fn read_config() -> Result<String> {
    let mut f = File::open("config.toml")
        .context("Failed to open config file")?;
    
    let mut s = String::new();
    f.read_to_string(&mut s)
        .context("Failed to read config file")?;
    
    Ok(s)
}

fn main() -> Result<()> {
    let config = read_config()?;
    println!("Config: {}", config);
    Ok(())
}
```

---

## 十、Option 与 Result 转换

```rust
fn find_user(id: u32) -> Option<User> {
    // ...
}

fn main() -> Result<(), MyError> {
    let user = find_user(1).ok_or(MyError::UserNotFound)?;
    Ok(())
}
```

---

## 十一、实战示例

```rust
use thiserror::Error;
use std::fs::File;
use std::io::Read;

#[derive(Error, Debug)]
enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Config missing: {0}")]
    ConfigMissing(String),
}

fn load_config(path: &str) -> Result<String, AppError> {
    let mut file = File::open(path)?;
    let mut content = String::new();
    file.read_to_string(&mut content)?;
    
    if content.is_empty() {
        return Err(AppError::ConfigMissing(path.to_string()));
    }
    
    Ok(content)
}

fn main() {
    match load_config("app.toml") {
        Ok(config) => println!("Loaded config: {}", config),
        Err(e) => println!("Error: {}", e),
    }
}
```

---

## 十二、最佳实践

1. 优先使用 Result 而非 panic
2. 使用 thiserror 定义自定义错误
3. 使用 anyhow 简化错误处理
4. 为错误提供有意义的上下文
5. 使用 ? 优雅地传播错误

---

## 十三、总结

Rust 的错误处理系统强大而灵活，合理使用能写出更健壮的代码。
