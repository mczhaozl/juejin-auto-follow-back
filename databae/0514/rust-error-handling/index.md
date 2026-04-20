# Rust 错误处理完全指南

## 一、Result

```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Cannot divide by zero".into())
    } else {
        Ok(a / b)
    }
}

fn main() {
    match divide(4.0, 2.0) {
        Ok(res) => println!("Result = {}", res),
        Err(e) => println!("Error = {}", e),
    }
}
```

## 二、? 运算符

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_file() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}
```

## 三、自定义错误

```rust
use std::fmt;

#[derive(Debug)]
struct MyError {
    msg: String,
}

impl fmt::Display for MyError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.msg)
    }
}
```

## 四、thiserror

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum MyError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("parse error: {0}")]
    Parse(#[from] std::num::ParseIntError),
}
```

## 最佳实践
- Result 作为标准错误类型
- ? 简化错误传播
- thiserror 定义错误类型
- anyhow/eyre 简化应用错误处理
- 不要过度使用 panic
