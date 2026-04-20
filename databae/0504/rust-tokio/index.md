# Rust Tokio 异步编程完全指南

## 一、Tokio 基础

```rust
// Cargo.toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }

#[tokio::main]
async fn main() {
    println!("Hello Tokio!");
}
```

## 二、异步函数

```rust
async fn say_hello() {
    println!("Hello!");
}

async fn greet() {
    say_hello().await;
}
```

## 三、并发任务

```rust
use tokio::task;

async fn task1() { /* ... */ }
async fn task2() { /* ... */ }

#[tokio::main]
async fn main() {
    let handle1 = task::spawn(task1());
    let handle2 = task::spawn(task2());
    
    handle1.await.unwrap();
    handle2.await.unwrap();
}
```

## 四、异步 IO

```rust
use tokio::fs;

async fn read_file() -> String {
    let content = fs::read_to_string("file.txt").await.unwrap();
    content
}
```

## 五、网络编程

```rust
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    let listener = TcpListener::bind("127.0.0.1:8080").await.unwrap();
    
    loop {
        let (socket, _) = listener.accept().await.unwrap();
        tokio::spawn(async move {
            // 处理连接
        });
    }
}
```

## 六、异步 HTTP

```rust
use reqwest;

async fn fetch_url() -> String {
    let resp = reqwest::get("https://example.com").await.unwrap();
    resp.text().await.unwrap()
}
```

## 七、Axum Web 框架

```rust
use axum::{routing::get, Router};
use axum::extract::State;

async fn hello() -> String {
    "Hello, Axum!".to_string()
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(hello));
    
    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_svc())
        .await.unwrap();
}
```

## 八、最佳实践

- 使用 async/await 语法
- 合理设计任务调度
- 处理错误和 panic
- 使用适当的 buffer 大小
- 监控和调试异步代码
