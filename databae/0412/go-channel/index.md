# Go Channel 完全指南：通道类型与缓冲机制

> 深入讲解 Go Channel，包括无缓冲通道、缓冲通道、单向通道、select 用法，以及 Channel 的底层实现和最佳实践。

## 一、Channel 基础

### 1.1 通道类型

```go
// 无整型通道
ch := make(chan int)

// 字符串通道
ch := make(chan string)

// 结构体通道
type Result struct {
    Code int
    Msg  string
}
ch := make(chan Result)
```

### 1.2 发送接收

```go
ch := make(chan int)

// 发送
ch <- 10

// 接收
num := <-ch

// 带箭头接收
<-ch  // 只接收，不保存
```

## 二、缓冲 Channel

### 2.1 有缓冲通道

```go
// 容量为 3 的缓冲通道
ch := make(chan int, 3)

// 发送（不阻塞，直到缓冲区满）
ch <- 1
ch <- 2
ch <- 3
// ch <- 4  // 阻塞
```

### 2.2 缓冲区使用场景

```go
// 并发任务缓冲
jobs := make(chan Job, 100)
results := make(chan Result, 100)
```

## 三、单向 Channel

### 3.1 只发送

```go
func send(ch chan<- int) {
    ch <- 42  // 可以发送
    // <-ch   // 编译错误，不能接收
}
```

### 3.2 只接收

```go
func receive(ch <-chan int) {
    num := <-ch  // 可以接收
    // ch <- 10  // 编译错误，不能发送
}
```

### 3.3 转换

```go
ch := make(chan int)

// 转换为只发送
sendOnly := chan<- int(ch)

// 转换为只接收
recvOnly := <-chan int(ch)
```

## 四、Select 用法

### 4.1 多通道选择

```go
select {
case msg1 := <-ch1:
    fmt.Println("收到 ch1:", msg1)
case msg2 := <-ch2:
    fmt.Println("收到 ch2:", msg2)
case ch3 <- data:
    fmt.Println("发送到 ch3")
}
```

### 4.2 超时处理

```go
select {
case msg := <-ch:
    fmt.Println("收到:", msg)
case <-time.After(time.Second):
    fmt.Println("超时")
}
```

### 4.3 退出信号

```go
done := make(chan struct{})

go func() {
    for {
        select {
        case <-done:
            return
        default:
            // 处理任务
        }
    }
}()

// 发送退出信号
close(done)
```

## 五、Channel 关闭

### 5.1 关闭原则

```go
ch := make(chan int)

// 发送方关闭
close(ch)

// 接收方检测
for {
    num, ok := <-ch
    if !ok {
        break  // 通道已关闭
    }
    fmt.Println(num)
}
```

### 5.2 range 遍历

```go
ch := make(chan int, 5)
ch <- 1
ch <- 2
ch <- 3
close(ch)

// 使用 range 遍历
for num := range ch {
    fmt.Println(num)
}
```

## 六、实战案例

### 6.1 扇入扇出

```go
// 扇入：多个通道合并到一个
func fanIn(chs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    result := make(chan int)
    
    output := func(ch <-chan int) {
        defer wg.Done()
        for n := range ch {
            result <- n
        }
    }
    
    wg.Add(len(chs))
    for _, ch := range chs {
        go output(ch)
    }
    
    go func() {
        wg.Wait()
        close(result)
    }()
    
    return result
}
```

### 6.2 管道

```go
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// 使用管道
nums := generate(1, 2, 3, 4, 5)
squares := square(nums)
for s := range squares {
    fmt.Println(s)
}
```

## 七、总结

Go Channel 核心要点：

1. **无缓冲**：同步通信
2. **缓冲通道**：异步通信
3. **单向通道**：类型安全
4. **Select**：多路复用
5. **关闭**：close 和 range
6. **模式**：扇入扇出、管道

掌握这些，Go 并发更精通！

---

**推荐阅读**：
- [Go Channel 官方博客](https://go.dev/blog/pipelines)

**如果对你有帮助，欢迎点赞收藏！**
