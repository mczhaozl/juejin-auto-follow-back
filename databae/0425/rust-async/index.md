# Rust 异步编程完全实战指南：从 Future 到 async/await

Rust 的异步编程是高性能 I/O 应用的关键。本文将带你从基础原理到实战项目，全面掌握 Rust 异步编程。

## 一、异步基础

### 1. 同步 vs 异步

```rust
// 同步代码
fn sync_read_file() -> String {
    std::fs::read_to_string("file.txt").unwrap()
}

// 异步代码（tokio）
async fn async_read_file() -> String {
    tokio::fs::read_to_string("file.txt").await.unwrap()
}
```

### 2. Future trait

```rust
pub trait Future {
    type Output;
    
    fn poll(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>
    ) -> Poll<Self::Output>;
}

pub enum Poll<T> {
    Ready(T),
    Pending,
}

// 简单的 Future 实现
struct MyFuture {
    count: i32,
}

impl Future for MyFuture {
    type Output = i32;
    
    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
        if self.count < 3 {
            self.count += 1;
            Poll::Pending
        } else {
            Poll::Ready(self.count)
        }
    }
}

async fn use_my_future() {
    let fut = MyFuture { count: 0 };
    let result = fut.await;
    println!("Result: {}", result);
}
```

### 3. async/await 语法

```rust
async fn foo() {
    println!("Hello from foo");
}

async fn bar() {
    foo().await;
    println!("Hello from bar");
}

async fn combine() {
    let a = async { 1 };
    let b = async { 2 };
    let (x, y) = tokio::join!(a, b);
    println!("{} + {}", x, y);
}
```

## 二、Tokio 运行时

### 1. 安装 Tokio

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }
```

### 2. 基础使用

```rust
#[tokio::main]
async fn main() {
    let result = async_read_file().await;
    println!("File content: {}", result);
}

// 多线程运行时
#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
async fn main() {
    // ...
}

// 当前线程运行时
#[tokio::main(flavor = "current_thread")]
async fn main() {
    // ...
}
```

### 3. 任务（Tasks）

```rust
#[tokio::main]
async fn main() {
    let handle1 = tokio::spawn(async {
        for i in 0..5 {
            println!("Task 1: {}", i);
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }
    });
    
    let handle2 = tokio::spawn(async {
        for i in 0..5 {
            println!("Task 2: {}", i);
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }
    });
    
    let _ = handle1.await;
    let _ = handle2.await;
}
```

### 4. Join! 和 Select!

```rust
use tokio::join;

async fn task1() -> i32 {
    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
    1
}

async fn task2() -> i32 {
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    2
}

#[tokio::main]
async fn main() {
    let (a, b) = join!(task1(), task2());
    println!("a = {}, b = {}", a, b);
}

// select! 宏
use tokio::select;

#[tokio::main]
async fn main() {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(1));
    let mut count = 0;
    
    loop {
        select! {
            _ = interval.tick() => {
                count += 1;
                println!("Tick {}", count);
                if count >= 5 {
                    break;
                }
            }
        }
    }
}
```

## 三、异步 I/O

### 1. 文件操作

```rust
use tokio::fs;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    // 读取文件
    let content = fs::read_to_string("file.txt").await?;
    println!("Content: {}", content);
    
    // 写入文件
    fs::write("output.txt", "Hello, Tokio!").await?;
    
    // 创建目录
    fs::create_dir_all("data").await?;
    
    Ok(())
}
```

### 2. TCP 服务器

```rust
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    println!("Server listening on 127.0.0.1:8080");
    
    loop {
        let (mut socket, addr) = listener.accept().await?;
        println!("New connection from {}", addr);
        
        tokio::spawn(async move {
            let mut buffer = [0; 1024];
            
            loop {
                let n = match socket.read(&mut buffer).await {
                    Ok(n) if n == 0 => break,
                    Ok(n) => n,
                    Err(e) => {
                        eprintln!("Read error: {}", e);
                        break;
                    }
                };
                
                println!("Received: {}", String::from_utf8_lossy(&buffer[..n]));
                
                if let Err(e) = socket.write_all(&buffer[..n]).await {
                    eprintln!("Write error: {}", e);
                    break;
                }
            }
        });
    }
}
```

### 3. TCP 客户端

```rust
use tokio::net::TcpStream;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let mut stream = TcpStream::connect("127.0.0.1:8080").await?;
    println!("Connected to server");
    
    stream.write_all(b"Hello from client!").await?;
    
    let mut buffer = [0; 1024];
    let n = stream.read(&mut buffer).await?;
    println!("Received: {}", String::from_utf8_lossy(&buffer[..n]));
    
    Ok(())
}
```

### 4. HTTP 服务器（Axum）

```toml
# Cargo.toml
[dependencies]
axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
```

```rust
use axum::{
    routing::{get, post},
    http::StatusCode,
    Json, Router,
};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct User {
    id: u32,
    name: String,
    email: String,
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(hello))
        .route("/users", post(create_user))
        .route("/users/:id", get(get_user));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn hello() -> &'static str {
    "Hello, Axum!"
}

async fn create_user(Json(user): Json<User>) -> (StatusCode, Json<User>) {
    println!("Created user: {:?}", user);
    (StatusCode::CREATED, Json(user))
}

async fn get_user(axum::extract::Path(id): axum::extract::Path<u32>) -> Json<User> {
    Json(User {
        id,
        name: "John Doe".to_string(),
        email: "john@example.com".to_string(),
    })
}
```

## 四、异步同步（Send + Sync）

### 1. Send trait

```rust
// Send: 可以在线程间传递所有权
use std::thread;

fn is_send<T: Send>() {}

struct MyType;

// MyType 自动实现 Send（如果它的所有字段都是 Send）

fn main() {
    is_send::<MyType>();  // 编译通过
    
    let data = vec![1, 2, 3];
    let handle = thread::spawn(move || {
        println!("{:?}", data);
    });
    handle.join().unwrap();
}
```

### 2. Sync trait

```rust
// Sync: 可以在线程间安全地共享引用
fn is_sync<T: Sync>() {}

use std::sync::Arc;

fn main() {
    is_sync::<String>();  // 编译通过
    
    let data = Arc::new(vec![1, 2, 3]);
    let data2 = data.clone();
    
    let handle = thread::spawn(move || {
        println!("{:?}", data2);
    });
    
    println!("{:?}", data);
    handle.join().unwrap();
}
```

### 3. 共享状态

```rust
use std::sync::{Arc, Mutex};
use tokio::sync::Semaphore;

#[tokio::main]
async fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..10 {
        let counter = counter.clone();
        let handle = tokio::spawn(async move {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.await.unwrap();
    }
    
    println!("Result: {}", *counter.lock().unwrap());
}
```

### 4. tokio::sync 原语

```rust
use tokio::sync::{Mutex, RwLock, Semaphore, mpsc, oneshot, watch};

#[tokio::main]
async fn main() {
    // Mutex
    let mutex = Mutex::new(0);
    *mutex.lock().await = 1;
    
    // RwLock
    let rwlock = RwLock::new(0);
    *rwlock.write().await = 1;
    let r = rwlock.read().await;
    println!("{}", *r);
    
    // mpsc channel
    let (tx, mut rx) = mpsc::channel(32);
    tokio::spawn(async move {
        tx.send("Hello").await.unwrap();
    });
    while let Some(msg) = rx.recv().await {
        println!("{}", msg);
    }
    
    // oneshot channel
    let (tx, rx) = oneshot::channel();
    tokio::spawn(async move {
        tx.send("Hello").unwrap();
    });
    let msg = rx.await.unwrap();
    println!("{}", msg);
}
```

## 五、错误处理

```rust
use tokio::fs;
use std::io;

async fn read_file_or_default() -> String {
    match fs::read_to_string("file.txt").await {
        Ok(content) => content,
        Err(e) if e.kind() == io::ErrorKind::NotFound => {
            "Default content".to_string()
        }
        Err(e) => panic!("Error reading file: {}", e),
    }
}

// 使用 ? 运算符
async fn process_file() -> io::Result<String> {
    let content = fs::read_to_string("file.txt").await?;
    Ok(content.to_uppercase())
}

#[tokio::main]
async fn main() -> io::Result<()> {
    let result = process_file().await?;
    println!("{}", result);
    Ok(())
}
```

## 六、实战项目：异步聊天服务器

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

```rust
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{mpsc, broadcast};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
enum Message {
    Join { username: String },
    Chat { from: String, text: String },
    Leave { username: String },
}

type Tx = mpsc::UnboundedSender<String>;
type Rx = mpsc::UnboundedReceiver<String>;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:8080").await?;
    println!("Chat server running on 0.0.0.0:8080");
    
    let (tx, _) = broadcast::channel(16);
    
    loop {
        let (socket, addr) = listener.accept().await?;
        let tx = tx.clone();
        
        tokio::spawn(async move {
            if let Err(e) = handle_connection(socket, tx).await {
                eprintln!("Connection error: {}", e);
            }
        });
    }
}

async fn handle_connection(
    mut stream: TcpStream,
    tx: broadcast::Sender<String>,
) -> std::io::Result<()> {
    let (reader, mut writer) = stream.split();
    let mut reader = BufReader::new(reader);
    let mut rx = tx.subscribe();
    
    let mut line = String::new();
    reader.read_line(&mut line).await?;
    let username = line.trim().to_string();
    
    tx.send(format!("{} joined the chat", username))?;
    
    let (user_tx, mut user_rx) = mpsc::unbounded_channel();
    
    tokio::spawn(async move {
        while let Some(msg) = user_rx.recv().await {
            if let Err(e) = writer.write_all(msg.as_bytes()).await {
                eprintln!("Write error: {}", e);
                break;
            }
        }
    });
    
    loop {
        tokio::select! {
            result = reader.read_line(&mut line) => {
                if result? == 0 {
                    break;
                }
                let msg = format!("{}: {}", username, line.trim());
                tx.send(msg)?;
                line.clear();
            }
            result = rx.recv() => {
                if let Ok(msg) = result {
                    user_tx.send(msg + "\n")?;
                }
            }
        }
    }
    
    tx.send(format!("{} left the chat", username))?;
    Ok(())
}
```

## 七、最佳实践

1. 使用 #[tokio::main] 宏
2. 避免在 async 中使用阻塞操作
3. 使用 tokio::spawn 创建任务
4. 合理使用 join! 和 select!
5. 注意 Send 和 Sync trait
6. 使用 tokio::sync 原语
7. 错误处理要完善
8. 合理配置运行时参数
9. 监控任务运行状态
10. 使用 tracing 记录日志

## 八、总结

Rust 异步编程核心要点：
- 理解 Future trait 和 Poll 枚举
- 使用 async/await 语法
- 掌握 Tokio 运行时
- 异步 I/O 操作（文件、网络）
- Send 和 Sync trait
- 共享状态原语（Mutex、RwLock、channel）
- 错误处理
- 实战项目（聊天服务器）

开始用 Rust 异步编程构建高性能应用吧！
