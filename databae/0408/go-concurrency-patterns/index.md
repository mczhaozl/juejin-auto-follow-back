# Go 并发模式实战：goroutine、channel 与经典并发模式详解

> 深入讲解 Go 语言并发编程，包括 goroutine、channel 的使用，以及生产者-消费者、扇入扇出等经典并发模式。

## 一、Go 并发基础

### 1.1 goroutine

goroutine 是 Go 的轻量级线程，由 Go 运行时管理：

```go
func sayHello(name string) {
    fmt.Println("Hello,", name)
}

func main() {
    go sayHello("张三")
    go sayHello("李四")
    time.Sleep(time.Second)
}
```

### 1.2 channel

channel 是 goroutine 之间的通信机制：

```go
ch := make(chan int)

// 发送
go func() {
    ch <- 42
}()

// 接收
result := <-ch
```

## 二、经典并发模式

### 2.1 生产者-消费者

```go
func producer(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for n := range ch {
        fmt.Println("Received:", n)
    }
}

func main() {
    ch := make(chan int)
    go producer(ch)
    consumer(ch)
}
```

### 2.2 带缓冲的 channel

```go
// 缓冲大小为 3
ch := make(chan int, 3)

// 发送时不会阻塞，直到缓冲区满
ch <- 1
ch <- 2
ch <- 3
ch <- 4 // 这里才会阻塞
```

### 2.3 select 多路复用

```go
func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(time.Second)
        ch1 <- "one"
    }()

    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "two"
    }()

    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            fmt.Println("received:", msg1)
        case msg2 := <-ch2:
            fmt.Println("received:", msg2)
        }
    }
}
```

### 2.4 超时处理

```go
func withTimeout(ch <-chan string, timeout time.Duration) (string, bool) {
    select {
    case msg := <-ch:
        return msg, true
    case <-time.After(timeout):
        return "", false
    }
}
```

## 三、Worker Pool 模式

### 3.1 基本实现

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for job := range jobs {
        fmt.Printf("worker %d processing job %d\n", id, job)
        time.Sleep(time.Second) // 模拟工作
        results <- job * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动 3 个 worker
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    // 发送 9 个任务
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)

    // 收集结果
    for r := 1; r <= 9; r++ {
        <-results
    }
}
```

### 3.2 带上下文的 Worker

```go
func workerWithContext(ctx context.Context, id int, jobs <-chan int, results chan<- int) {
    for {
        select {
        case <-ctx.Done():
            fmt.Printf("Worker %d stopped\n", id)
            return
        case job, ok := <-jobs:
            if !ok {
                return
            }
            fmt.Printf("Worker %d processing job %d\n", id, job)
            results <- job * 2
        }
    }
}
```

## 四、扇入扇出模式

### 4.1 扇出：多个 goroutine 处理同一任务

```go
func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动多个 worker（扇出）
    for w := 1; w <= 5; w++ {
        go worker(w, jobs, results)
    }

    // 发送任务
    go func() {
        for j := 1; j <= 20; j++ {
            jobs <- j
        }
        close(jobs)
    }()

    // 收集结果
    go func() {
        for r := 1; r <= 20; r++ {
            fmt.Println(<-results)
        }
    }()

    time.Sleep(5 * time.Second)
}
```

### 4.2 扇入：合并多个 channel

```go
func fanIn(channels ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    combined := make(chan int)

    output := func(ch <-chan int) {
        defer wg.Done()
        for n := range ch {
            combined <- n
        }
    }

    wg.Add(len(channels))
    for _, ch := range channels {
        go output(ch)
    }

    go func() {
        wg.Wait()
        close(combined)
    }()

    return combined
}
```

## 五、Context 取消模式

### 5.1 基础用法

```go
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    
    go func() {
        time.Sleep(2 * time.Second)
        cancel() // 取消所有子操作
    }()

    doWork(ctx)
}

func doWork(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            fmt.Println("Work cancelled:", ctx.Err())
            return
        default:
            fmt.Println("Working...")
            time.Sleep(500 * time.Millisecond)
        }
    }
}
```

### 5.2 WithTimeout 和 WithDeadline

```go
func fetchWithTimeout(url string, timeout time.Duration) (string, error) {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    client := &http.Client{}
    resp, err := client.Do(req)
    
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()
    
    body, _ := io.ReadAll(resp.Body)
    return string(body), nil
}
```

## 六、errgroup 并发模式

### 6.1 基础用法

```go
import "golang.org/x/sync/errgroup"

func main() {
    g := errgroup.Group{}
    
    urls := []string{
        "https://example.com",
        "https://example.org",
        "https://example.net",
    }

    results := make([]string, len(urls))

    for i, url := range urls {
        g.Go(func() error {
            resp, err := http.Get(url)
            if err != nil {
                return err
            }
            defer resp.Body.Close()
            
            body, err := io.ReadAll(resp.Body)
            if err != nil {
                return err
            }
            
            results[i] = string(body)
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        fmt.Println("Error:", err)
    }
}
```

### 6.2 带并发的 errgroup

```go
func processWithConcurrency(items []Item) ([]Result, error) {
    g, ctx := errgroup.WithContext(context.Background())
    
    results := make([]Result, len(items))
    
    for i, item := range items {
        i, item := i, item // 捕获变量
        g.Go(func() error {
            select {
            case <-ctx.Done():
                return ctx.Err()
            default:
                result, err := processItem(item)
                if err != nil {
                    return err
                }
                results[i] = result
                return nil
            }
        })
    }
    
    if err := g.Wait(); err != nil {
        return nil, err
    }
    
    return results, nil
}
```

## 七、Mutex 和 atomic

### 7.1 sync.Mutex

```go
type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}
```

### 7.2 sync/atomic

```go
import "sync/atomic"

var counter int64

func Increment() {
    atomic.AddInt64(&counter, 1)
}

func Get() int64 {
    return atomic.LoadInt64(&counter)
}
```

## 八、总结

Go 并发核心模式：

1. **goroutine**：轻量级并发
2. **channel**：goroutine 通信
3. **select**：多路复用
4. **Worker Pool**：任务分发
5. **扇入扇出**：并行处理
6. **Context**：取消和超时
7. **errgroup**：错误处理
8. **Mutex/atomic**：状态同步

掌握这些模式，可以写出高效、健壮的 Go 并发程序。

---

**推荐阅读**：
- [Go 并发模式官方文档](https://go.dev/blog/pipelines)
- [Go 语言圣经 - 并发](https://books.studygolang.com/gopl-zh/ch8/ch8.html)

**如果对你有帮助，欢迎点赞收藏！**
