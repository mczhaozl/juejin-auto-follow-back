# Rust Async 完全指南

## 一、异步函数

```rust
async fn hello() {
    println!("Hello");
}

#[tokio::main]
async fn main() {
    hello().await;
}
```

## 二、Join

```rust
use tokio::task;

async fn task1() { /* ... */ }
async fn task2() { /* ... */ }

#[tokio::main]
async fn main() {
    let t1 = task::spawn(task1());
    let t2 = task::spawn(task2());
    
    t1.await.unwrap();
    t2.await.unwrap();
}
```

## 三、异步 IO

```rust
use tokio::fs::File;
use tokio::io::AsyncReadExt;

#[tokio::main]
async fn main() {
    let mut f = File::open("test.txt").await.unwrap();
    let mut content = String::new();
    f.read_to_string(&mut content).await.unwrap();
    println!("{}", content);
}
```

## 四、Stream

```rust
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    let mut stream = tokio_stream::iter(1..=10);
    
    while let Some(item) = stream.next().await {
        println!("{}", item);
    }
}
```

## 五、最佳实践

- 使用 Tokio 运行时
- 避免阻塞 async（使用 spawn_blocking）
- 合理使用 JoinHandle
- 处理错误（Result）
- 使用 tracing 记录日志
