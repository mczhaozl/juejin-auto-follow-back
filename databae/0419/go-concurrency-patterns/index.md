# Go 并发模式完全指南：channel、context 与模式实践

> 一句话摘要：深入解析 Go 语言并发编程的核心概念，涵盖 Goroutine、Channel、Context、Select 及常用并发模式，学习如何编写高效、安全的并发代码。

## 一、Go 并发基础

### 1.1 并发 vs 并行

Go 的并发模型基于 CSP（Communicating Sequential Processes）：

```
┌─────────────────────────────────────────────────────────┐
│                 并发 vs 并行                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  并发 (Concurrency):                                    │
│    ┌─────┐    ┌─────┐    ┌─────┐                      │
│    │ G1  │    │ G2  │    │ G3  │  ← 快速切换          │
│    └──┬──┘    └──┬──┘    └──┬──┘                      │
│       └──────────┴──────────┘                          │
│              单核 CPU                                   │
│                                                          │
│  并行 (Parallelism):                                    │
│    ┌─────┐ ┌─────┐ ┌─────┐                           │
│    │ G1  │ │ G2  │ │ G3  │  ← 同时执行                │
│    └──┬──┘ └──┬──┘ └──┬──┘                             │
│       └───────┴───────┘                                │
│          多核 CPU                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Goroutine 基础

```go
// 启动一个 goroutine
go func() {
    fmt.Println("在新的 goroutine 中执行")
}()

// 带参数的 goroutine
msg := "Hello"
go func(m string) {
    fmt.Println(m)
}(msg)

// 等待 goroutine 完成
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    fmt.Println("任务完成")
}()
wg.Wait()
```

### 1.3 Goroutine vs 线程

| 特性 | Goroutine | 线程 |
|------|-----------|------|
| 创建成本 | ~2KB | ~1-8MB |
| 切换成本 | ~200ns | ~1-2μs |
| 调度 | Go 运行时 (M:P:G) | OS 调度器 |
| 通信 | Channel | 共享内存 |

## 二、Channel 详解

### 2.1 Channel 基础

```go
// 创建无缓冲 channel
ch1 := make(chan int)

// 创建有缓冲 channel
ch2 := make(chan int, 10)

// 发送数据
ch <- 42

// 接收数据
value := <-ch

// 关闭 channel
close(ch)
```

### 2.2 单向 Channel

```go
// 生产者：只能发送
func producer(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)
}

// 消费者：只能接收
func consumer(ch <-chan int) {
    for v := range ch {
        fmt.Println("收到:", v)
    }
}

// 使用
ch := make(chan int)
go producer(ch)
consumer(ch)
```

### 2.3 Select 语句

```go
// select 用于监听多个 channel
select {
case v := <-ch1:
    fmt.Println("从 ch1 收到:", v)
case v := <-ch2:
    fmt.Println("从 ch2 收到:", v)
case ch3 <- 42:
    fmt.Println("发送到 ch3")
default:
    fmt.Println("所有 channel 都未就绪")
}
```

### 2.4 超时处理

```go
// 带超时的 select
func withTimeout(ch <-chan int, timeout time.Duration) (int, error) {
    select {
    case v := <-ch:
        return v, nil
    case <-time.After(timeout):
        return 0, errors.New("timeout")
    }
}

// 优雅关闭
func gracefulSelect(done <-chan struct{}, ch <-chan int) {
    select {
    case <-done:
        fmt.Println("收到关闭信号")
        return
    case v := <-ch:
        fmt.Println("收到数据:", v)
    }
}
```

## 三、Context 模式

### 3.1 Context 基础

```go
// 创建 context
ctx := context.Background()
ctx, cancel := context.WithCancel(ctx)
ctx, cancel = context.WithTimeout(ctx, 5*time.Second)
ctx, cancel = context.WithValue(ctx, "key", "value")

// 使用 context
select {
case <-ctx.Done():
    fmt.Println("Context 取消:", ctx.Err())
default:
    // 正常工作
}
```

### 3.2 传递请求上下文

```go
type User struct {
    ID   string
    Name string
}

func fetchUser(ctx context.Context, userID string) (*User, error) {
    // 注入 trace ID
    traceID := ctx.Value("trace_id")
    fmt.Println("Trace ID:", traceID)

    req, err := http.NewRequestWithContext(ctx, "GET", "/user/"+userID, nil)
    if err != nil {
        return nil, err
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    // ... 解析响应
    return &User{ID: userID, Name: "张三"}, nil
}

// 在 HTTP handler 中使用
func userHandler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    ctx = context.WithValue(ctx, "trace_id", getTraceID(r))

    user, err := fetchUser(ctx, "123")
    if err != nil {
        http.Error(w, err.Error(), 500)
        return
    }

    json.NewEncoder(w).Encode(user)
}
```

### 3.3 取消传播

```go
func worker(ctx context.Context, id int) {
    for {
        select {
        case <-ctx.Done():
            fmt.Printf("Worker %d 取消: %v\n", id, ctx.Err())
            return
        default:
            fmt.Printf("Worker %d 工作中...\n", id)
            time.Sleep(500 * time.Millisecond)
        }
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())

    for i := 1; i <= 3; i++ {
        go worker(ctx, i)
    }

    time.Sleep(2 * time.Second)
    fmt.Println("取消所有 worker")
    cancel()

    time.Sleep(1 * time.Second)
}
```

### 3.4 HTTP Server 生命周期

```go
func serverWithGracefulShutdown(addr string) error {
    srv := &http.Server{
        Addr: addr,
    }

    // 创建带超时的 context
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    // 启动服务器
    go func() {
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    // 等待中断信号
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
    <-sigChan

    // 优雅关闭
    return srv.Shutdown(ctx)
}
```

## 四、并发模式

### 4.1 生产者-消费者

```go
func producer(ch chan<- int, count int) {
    for i := 0; i < count; i++ {
        ch <- i
    }
    close(ch)
}

func consumer(id int, ch <-chan int, wg *sync.WaitGroup) {
    defer wg.Done()
    for v := range ch {
        fmt.Printf("Consumer %d: %d\n", id, v)
        time.Sleep(100 * time.Millisecond)
    }
}

func main() {
    ch := make(chan int, 100)
    var wg sync.WaitGroup

    // 1 个生产者
    go producer(ch, 1000)

    // 3 个消费者
    for i := 1; i <= 3; i++ {
        wg.Add(1)
        go consumer(i, ch, &wg)
    }

    wg.Wait()
    fmt.Println("完成")
}
```

### 4.2 管道（Pipeline）

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

func merge(cs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)

    output := func(c <-chan int) {
        for n := range c {
            out <- n
        }
        wg.Done()
    }

    wg.Add(len(cs))
    for _, c := range cs {
        go output(c)
    }

    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}

func main() {
    // 生成 -> 平方 -> 合并
    c1 := generate(1, 2, 3, 4, 5)
    c2 := generate(6, 7, 8, 9, 10)

    for n := range merge(square(c1), square(c2)) {
        fmt.Println(n)
    }
}
```

### 4.3 fan-out / fan-in

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("Worker %d 处理 job %d\n", id, j)
        time.Sleep(time.Second)
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动 3 个 worker
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    // 发送 9 个 job
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)

    // 收集结果
    for a := 1; a <= 9; a++ {
        <-results
    }
}
```

### 4.4 队列（Worker Pool）

```go
type Job struct {
    ID   int
    Data string
}

type Result struct {
    JobID  int
    Output string
}

func workerPool(numWorkers int, jobs <-chan Job, results chan<- Result) {
    var wg sync.WaitGroup

    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for job := range jobs {
                result := Result{
                    JobID:  job.ID,
                    Output: process(job),
                }
                results <- result
            }
        }(i)
    }

    wg.Wait()
    close(results)
}

func process(job Job) string {
    time.Sleep(100 * time.Millisecond)
    return fmt.Sprintf("处理了: %s", job.Data)
}

func main() {
    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    // 启动 worker pool
    go workerPool(5, jobs, results)

    // 发送任务
    go func() {
        for i := 1; i <= 50; i++ {
            jobs <- Job{ID: i, Data: fmt.Sprintf("数据-%d", i)}
        }
        close(jobs)
    }()

    // 收集结果
    for result := range results {
        fmt.Printf("Job %d 完成: %s\n", result.JobID, result.Output)
    }
}
```

### 4.5 信号量（Semaphore）

```go
type Semaphore struct {
    ch chan struct{}
}

func NewSemaphore(max int) *Semaphore {
    ch := make(chan struct{}, max)
    for i := 0; i < max; i++ {
        ch <- struct{}{}
    }
    return &Semaphore{ch: ch}
}

func (s *Semaphore) Acquire() {
    <-s.ch
}

func (s *Semaphore) Release() {
    s.ch <- struct{}{}
}

func main() {
    sem := NewSemaphore(3)

    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            sem.Acquire()
            defer sem.Release()

            fmt.Printf("Goroutine %d 开始\n", id)
            time.Sleep(time.Second)
            fmt.Printf("Goroutine %d 结束\n", id)
        }(i)
    }

    wg.Wait()
}
```

### 4.6 限流器（Rate Limiter）

```go
type RateLimiter struct {
    rate  int
    tokens int
    max   int
    mu    sync.Mutex
    cond  *sync.Cond
}

func NewRateLimiter(rate int) *RateLimiter {
    rl := &RateLimiter{
        rate:  rate,
        tokens: rate,
        max:   rate,
    }
    rl.cond = sync.NewCond(&rl.mu)
    go rl.replenish()
    return rl
}

func (rl *RateLimiter) replenish() {
    ticker := time.NewTicker(time.Second)
    for range ticker.C {
        rl.mu.Lock()
        rl.tokens = rl.max
        rl.cond.Broadcast()
        rl.mu.Unlock()
    }
}

func (rl *RateLimiter) Allow() bool {
    rl.mu.Lock()
    defer rl.mu.Unlock()

    for rl.tokens <= 0 {
        rl.cond.Wait()
    }

    rl.tokens--
    return true
}

// 使用
func main() {
    limiter := NewRateLimiter(10) // 每秒 10 个请求

    var wg sync.WaitGroup
    for i := 0; i < 20; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            if limiter.Allow() {
                fmt.Printf("请求 %d 通过\n", id)
            }
        }(i)
    }

    wg.Wait()
}
```

### 4.7 超时控制

```go
func doWithTimeout(ctx context.Context, task func() error) error {
    done := make(chan error, 1)

    go func() {
        done <- task()
    }()

    select {
    case err := <-done:
        return err
    case <-ctx.Done():
        return ctx.Err()
    }
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()

    err := doWithTimeout(ctx, func() error {
        time.Sleep(5 * time.Second)
        return nil
    })

    if err != nil {
        fmt.Println("任务失败:", err)
    }
}
```

## 五、同步原语

### 5.1 sync.Mutex

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

### 5.2 sync.RWMutex

```go
type SafeCache struct {
    mu    sync.RWMutex
    items map[string]string
}

func (c *SafeCache) Get(key string) string {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.items[key]
}

func (c *SafeCache) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = value
}
```

### 5.3 sync.Once

```go
type Config struct {
    Data string
}

var (
    config *Config
    once   sync.Once
)

func GetConfig() *Config {
    once.Do(func() {
        config = &Config{Data: "配置数据"}
    })
    return config
}
```

### 5.4 sync.Map

```go
var m sync.Map

// 存储
m.Store("key1", "value1")
m.Store("key2", "value2")

// 加载
if val, ok := m.Load("key1"); ok {
    fmt.Println(val)
}

// 删除
m.Delete("key1")

// 遍历
m.Range(func(key, value interface{}) bool {
    fmt.Printf("%s: %s\n", key, value)
    return true
})
```

### 5.5 sync.WaitGroup

```go
func processAll(items []int) []int {
    results := make([]int, len(items))
    var wg sync.WaitGroup

    for i, item := range items {
        wg.Add(1)
        go func(idx int, val int) {
            defer wg.Done()
            results[idx] = val * 2
        }(i, item)
    }

    wg.Wait()
    return results
}
```

## 六、错误处理

### 6.1 错误传播

```go
func task1() error {
    return errors.New("task1 失败")
}

func task2() error {
    return task1()
}

func main() {
    if err := task2(); err != nil {
        fmt.Println("错误:", err)
        // 包装错误
        fmt.Println("完整错误:", fmt.Errorf("task2 执行失败: %w", err))
    }
}
```

### 6.2 错误组

```go
func main() {
    var errs []error
    var mu sync.Mutex

    addError := func(err error) {
        mu.Lock()
        defer mu.Unlock()
        errs = append(errs, err)
    }

    var wg sync.WaitGroup
    wg.Add(3)

    go func() {
        defer wg.Done()
        if err := task1(); err != nil {
            addError(err)
        }
    }()

    go func() {
        defer wg.Done()
        if err := task2(); err != nil {
            addError(err)
        }
    }()

    go func() {
        defer wg.Done()
        if err := task3(); err != nil {
            addError(err)
        }
    }()

    wg.Wait()

    if len(errs) > 0 {
        for _, err := range errs {
            fmt.Println("错误:", err)
        }
    }
}
```

### 6.3 errgroup

```go
import "golang.org/x/sync/errgroup"

func main() {
    g := &errgroup.Group{}

    g.Go(func() error {
        return task1()
    })

    g.Go(func() error {
        return task2()
    })

    g.Go(func() error {
        return task3()
    })

    if err := g.Wait(); err != nil {
        fmt.Println("错误:", err)
    }
}
```

## 七、实战案例

### 7.1 并发爬虫

```go
type Result struct {
    URL  string
    Body string
}

func crawl(ctx context.Context, urls []string, concurrency int) ([]Result, error) {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    results := make([]Result, 0)
    var mu sync.Mutex

    jobs := make(chan string, len(urls))
    for _, url := range urls {
        jobs <- url
    }
    close(jobs)

    var wg sync.WaitGroup
    g, ctx := errgroup.WithContext(ctx)

    for i := 0; i < concurrency; i++ {
        wg.Add(1)
        g.Go(func() error {
            defer wg.Done()
            for url := range jobs {
                select {
                case <-ctx.Done():
                    return ctx.Err()
                default:
                    body, err := fetch(url)
                    if err != nil {
                        continue
                    }

                    mu.Lock()
                    results = append(results, Result{URL: url, Body: body})
                    mu.Unlock()
                }
            }
            return nil
        })
    }

    wg.Wait()

    if err := g.Wait(); err != nil {
        return results, err
    }

    return results, nil
}

func fetch(url string) (string, error) {
    resp, err := http.Get(url)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return "", err
    }

    return string(body), nil
}
```

### 7.2 并发数据库操作

```go
type BatchProcessor struct {
    db       *sql.DB
    workers  int
    batchSize int
}

func NewBatchProcessor(db *sql.DB, workers, batchSize int) *BatchProcessor {
    return &BatchProcessor{
        db:       db,
        workers:  workers,
        batchSize: batchSize,
    }
}

func (bp *BatchProcessor) Process(ctx context.Context, items []Item) error {
    jobs := make(chan []Item, (len(items)+bp.batchSize-1)/bp.batchSize)

    // 分批
    for i := 0; i < len(items); i += bp.batchSize {
        end := i + bp.batchSize
        if end > len(items) {
            end = len(items)
        }
        jobs <- items[i:end]
    }
    close(jobs)

    g, ctx := errgroup.WithContext(ctx)

    for i := 0; i < bp.workers; i++ {
        g.Go(func() error {
            for batch := range jobs {
                select {
                case <-ctx.Done():
                    return ctx.Err()
                default:
                    if err := bp.processBatch(ctx, batch); err != nil {
                        return err
                    }
                }
            }
            return nil
        })
    }

    return g.Wait()
}

func (bp *BatchProcessor) processBatch(ctx context.Context, items []Item) error {
    tx, err := bp.db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    defer tx.Rollback()

    stmt, err := tx.PrepareContext(ctx,
        "INSERT INTO items (id, data) VALUES (?, ?)")
    if err != nil {
        return err
    }
    defer stmt.Close()

    for _, item := range items {
        _, err := stmt.ExecContext(ctx, item.ID, item.Data)
        if err != nil {
            return err
        }
    }

    return tx.Commit()
}
```

### 7.3 心跳检测

```go
type Heartbeat struct {
    interval time.Duration
    timeout  time.Duration
    ch       chan struct{}
    mu       sync.Mutex
    stopped  bool
}

func NewHeartbeat(interval, timeout time.Duration) *Heartbeat {
    return &Heartbeat{
        interval: interval,
        timeout:  timeout,
        ch:       make(chan struct{}),
    }
}

func (h *Heartbeat) Start() {
    go func() {
        ticker := time.NewTicker(h.interval)
        defer ticker.Stop()

        for {
            select {
            case <-ticker.C:
                h.mu.Lock()
                if h.stopped {
                    h.mu.Unlock()
                    return
                }
                h.mu.Unlock()

                // 发送心跳
                select {
                case h.ch <- struct{}{}:
                default:
                }

                // 检查超时
                timeout := time.After(h.timeout)
                select {
                case <-h.ch:
                    // 收到响应
                case <-timeout:
                    fmt.Println("心跳超时")
                case <-h.ch:
                }
            }
        }
    }()
}

func (h *Heartbeat) Stop() {
    h.mu.Lock()
    h.stopped = true
    h.mu.Unlock()
    close(h.ch)
}
```

## 八、最佳实践

### 8.1 避免死锁

```go
// ❌ 可能死锁：channel 在主 goroutine 关闭
func badClose() {
    ch := make(chan int)
    go func() {
        for i := range ch {
            fmt.Println(i)
        }
    }()
    close(ch) // 可能还没开始监听
}

// ✅ 正确：等待 goroutine 完成后再关闭
func goodClose() {
    ch := make(chan int)
    var wg sync.WaitGroup
    wg.Add(1)

    go func() {
        defer wg.Done()
        for i := range ch {
            fmt.Println(i)
        }
    }()

    close(ch)
    wg.Wait()
}

// ❌ 可能死锁：互斥锁顺序不一致
func badLockOrder(a, b *sync.Mutex) {
    a.Lock()
    b.Lock()
    // ...
    a.Unlock()
    b.Unlock()
}

// ✅ 正确：总是按固定顺序加锁
func goodLockOrder(a, b *sync.Mutex) {
    // 按地址排序
    if a > b {
        a, b = b, a
    }

    a.Lock()
    b.Lock()
    // ...
    b.Unlock()
    a.Unlock()
}
```

### 8.2 资源清理

```go
func withCleanup() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel() // 确保清理

    ch := make(chan int)
    var wg sync.WaitGroup

    // 启动 worker
    wg.Add(1)
    go func() {
        defer wg.Done()
        for {
            select {
            case <-ctx.Done():
                return
            case v := <-ch:
                fmt.Println(v)
            }
        }
    }()

    // 发送数据
    ch <- 1
    ch <- 2

    // 清理
    cancel() // 通知 worker 退出
    wg.Wait()
    close(ch)
}
```

### 8.3 调试技巧

```go
import (
    "runtime"
    "runtime/pprof"
)

// 打印 goroutine 堆栈
func printStacks() {
    buf := make([]byte, 1<<20)
    n := runtime.Stack(buf, true)
    fmt.Printf("Goroutine 堆栈:\n%s\n", buf[:n])
}

// 导出 pprof 数据
func enablePProf() {
    go func() {
        http.ListenAndServe(":6060", nil)
    }()

    // 或导出到文件
    f, _ := os.Create("cpu.prof")
    pprof.StartCPUProfile(f)
    defer pprof.StopCPUProfile()
}
```

## 九、总结

### 9.1 核心要点

1. **Goroutine 是 Go 并发的核心，轻量且高效**
2. **Channel 是 goroutine 间通信的首选方式**
3. **Context 用于取消信号和超时控制**
4. **sync 包提供互斥锁、读写锁、WaitGroup 等同步原语**
5. **errgroup 简化多任务错误处理**

### 9.2 常用模式

| 模式 | 适用场景 |
|------|---------|
| Producer-Consumer | 任务队列处理 |
| Pipeline | 数据流处理 |
| Worker Pool | 固定并发数处理 |
| Semaphore | 限流控制 |
| Context | 超时和取消 |

### 9.3 资源链接

- [Go Concurrency Patterns](https://go.dev/blog/concurrency)
- [golang.org/x/sync/errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup)
- [Go Context](https://go.dev/blog/context)

> 如果对你有帮助，欢迎点赞、收藏！有任何问题欢迎在评论区讨论。
