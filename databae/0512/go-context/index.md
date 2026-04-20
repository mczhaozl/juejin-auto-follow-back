# Go Context 完全指南

## 一、基础 Context

```go
package main

import (
  "context"
  "fmt"
  "time"
)

func main() {
  // Background() - 根 Context
  ctx := context.Background()
  doWork(ctx)
  
  // TODO() - 占位 Context
  ctx2 := context.TODO()
  doWork(ctx2)
}

func doWork(ctx context.Context) {
  fmt.Println("Working...")
}
```

## 二、取消 Context

```go
// 1. WithCancel
func withCancelExample() {
  ctx, cancel := context.WithCancel(context.Background())
  
  go func() {
    time.Sleep(2 * time.Second)
    cancel() // 2 秒后取消
  }()
  
  doSomething(ctx)
}

// 2. WithTimeout
func withTimeoutExample() {
  ctx, cancel := context.WithTimeout(
    context.Background(), 
    3*time.Second
  )
  defer cancel()
  
  doSomething(ctx)
}

// 3. WithDeadline
func withDeadlineExample() {
  deadline := time.Now().Add(5 * time.Second)
  ctx, cancel := context.WithDeadline(context.Background(), deadline)
  defer cancel()
  
  doSomething(ctx)
}
```

## 三、传递值

```go
// 1. WithValue
type key string

func withValueExample() {
  ctx := context.Background()
  ctx = context.WithValue(ctx, key("user"), "Alice")
  ctx = context.WithValue(ctx, key("age"), 30)
  
  printValue(ctx, key("user"))
  printValue(ctx, key("age"))
}

func printValue(ctx context.Context, k key) {
  if v := ctx.Value(k); v != nil {
    fmt.Printf("%s: %v\n", k, v)
  }
}
```

## 四、监听 Context

```go
func doSomething(ctx context.Context) {
  for {
    select {
    case <-ctx.Done():
      fmt.Println("Canceled:", ctx.Err())
      return
    case <-time.After(500 * time.Millisecond):
      fmt.Println("Still working...")
    }
  }
}
```

## 最佳实践
- Context 第一个参数
- 使用 WithCancel 管理生命周期
- WithTimeout 防止泄漏
- Value 只用于请求作用域数据
- 不要在 Context 存储可选参数
