# Rust Axum Web 框架完全指南

## 一、Axum 基础

```rust
// Cargo.toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
```

```rust
use axum::{routing::get, Router};

async fn hello_world() -> &'static str {
    "Hello, Axum!"
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(hello_world));
    
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

## 二、路径参数

```rust
use axum::{extract::Path, http::StatusCode};

async fn user_profile(Path(user_id): Path<u64>) -> String {
    format!("User profile for: {}", user_id)
}

let app = Router::new()
    .route("/users/:user_id", get(user_profile));
```

## 三、JSON 请求和响应

```rust
use axum::{extract::Json};
use serde::Deserialize;

#[derive(Deserialize)]
struct CreateUser {
    name: String,
    email: String,
}

async fn create_user(Json(user): Json<CreateUser>) -> (StatusCode, Json<serde_json::Value>) {
    let user = serde_json::json!({
        "id": 1,
        "name": user.name,
        "email": user.email,
    });
    
    (StatusCode::CREATED, Json(user))
}
```

## 四、查询参数

```rust
use axum::extract::Query;
use serde::Deserialize;

#[derive(Deserialize)]
struct ListParams {
    page: Option<usize>,
    limit: Option<usize>,
}

async fn list_users(Query(params): Query<ListParams>) -> String {
    format!("Page: {:?}, Limit: {:?}", params.page, params.limit)
}
```

## 五、状态管理

```rust
use axum::extract::State;
use std::sync::Arc;

struct AppState {
    db: Db,
}

async fn get_state(State(state): State<Arc<AppState>>) -> String {
    "State accessed".to_string()
}

let state = Arc::new(AppState { db: Db::new() });
let app = Router::new()
    .with_state(state);
```

## 六、中间件

```rust
use axum::{middleware, handler::HandlerWithoutStateExt};

async fn logging_layer<B>(
    req: Request<B>,
    next: Next<B>,
) -> Result<Response, StatusCode> {
    println!("Request: {:?}", req.uri());
    let resp = next.run(req).await;
    Ok(resp)
}

let app = Router::new()
    .layer(middleware::from_fn(logging_layer));
```

## 七、错误处理

```rust
use axum::{response::IntoResponse, http::StatusCode};

enum AppError {
    NotFound,
    InternalError,
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        match self {
            AppError::NotFound => {
                (StatusCode::NOT_FOUND, "Not found").into_response()
            }
            AppError::InternalError => {
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal error").into_response()
            }
        }
    }
}
```

## 八、实战应用

```rust
// 完整应用示例
#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(hello))
        .route("/users", get(list_users).post(create_user))
        .route("/users/:id", get(get_user));
    
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

## 九、最佳实践

- 使用合适的 extractors 提取数据
- 实现统一的错误处理
- 使用状态管理共享资源
- 添加适当的中间件
- 测试端点
- 性能监控和优化
