# Go 并发编程完全指南：Goroutine 与 Mutex

> 深入讲解 Go 并发编程，包括 Goroutine、Channel、WaitGroup、Mutex，以及并发安全和实际项目中的并发模式。

## 一、Goroutine

### 1.1 基础用法

```go
func main() {
    // 启动 goroutine
    go say("Hello")
    go say("World")
    
    time.Sleep(time.Second)
}

func say(s string) {
    fmt.Println(s)
}
```

### 1.2 匿名函数

```go
go func() {
    fmt.Println("异步执行")
}()

go func(msg string) {
    fmt.Println(msg)
}("参数传递")
```

## 二、Channel

### 2.1 创建通道

```go
// 无缓冲通道
ch := make(chan int)

// 有缓冲通道
ch := make(chan int, 10)
```

### 2.2 发送和接收

```go
ch := make(chan int)

// 发送
ch <- 42

// 接收
value := <-ch
```

### 2.3 关闭通道

```go
close(ch)

// 检测通道是否关闭
v, ok := <-ch
if !ok {
    fmt.Println("通道已关闭")
}
```

## 三、Select

### 3.1 多通道监听

```go
select {
case msg1 := <-ch1:
    fmt.Println("收到:", msg1)
case msg2 := <-ch2:
    fmt.Println("收到:", msg2)
case <-time.After(time.Second):
    fmt.Println("超时")
}
```

### 3.2 非阻塞接收

```go
select {
case msg := <-ch:
    fmt.Println(msg)
default:
    fmt.Println("无数据")
}
```

## 四、WaitGroup

### 4.1 等待组

```go
var wg sync.WaitGroup

func worker(id int) {
    defer wg.Done()
    fmt.Printf("Worker %d 完成\n", id)
}

func main() {
    for i := 1; i <= 5; i++ {
        wg.Add(1)
        go worker(i)
    }
    wg.Wait()  // 等待所有任务完成
    fmt.Println("所有任务完成")
}
```

## 五、Mutex

### 5.1 互斥锁

```go
var (
    counter int
    mutex   sync.Mutex
)

func increment() {
    mutex.Lock()
    defer mutex.Unlock()
    counter++
}
```

### 5.2 读写锁

```go
var (
    data   map[string]string
    rwMutex sync.RWMutex
)

func read(key string) string {
    rwMutex.RLock()
    defer rwMutex.RUnlock()
    return data[key]
}

func write(key, value string) {
    rwMutex.Lock()
    defer rwMutex.Unlock()
    data[key] = value
}
```

## 六、实战案例

### 6.1 并发抓取

```go
func fetch(urls []string) []string {
    results := make(chan string, len(urls))
    var wg sync.WaitGroup
    
    for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()
            resp, _ := http.Get(u)
            defer resp.Body.Close()
            results <- u
        }(url)
    }
    
    go func() {
        wg.Wait()
        close(results)
    }()
    
    var outputs []string
    for r := range results {
        outputs = append(outputs, r)
    }
    return outputs
}
```

### 6.2 工作池

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("worker %d 处理 %d\n", id, j)
        time.Sleep(time.Millisecond * 100)
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)
    
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }
    
    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)
    
    for a := 1; a <= 5; a++ {
        <-results
    }
}
```

## 七、总结

Go 并发核心要点：

1. **Goroutine**：轻量级线程
2. **Channel**：通信机制
3. **Select**：多通道监听
4. **WaitGroup**：任务同步
5. **Mutex**：互斥访问
6. **RWMutex**：读写分离

掌握这些，Go 并发不再难！

---

**推荐阅读**：
- [Go 并发文档](https://go.dev/doc/articles/concurrency)

**如果对你有帮助，欢迎点赞收藏！**
