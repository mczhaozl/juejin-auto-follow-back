# Go 并发进阶与高级模式完全指南：从原理到实战

## 一、Goroutine 池

```go
package main

import (
    "fmt"
    "sync"
)

func worker(id int, jobs <-chan int, results chan<- int, wg *sync.WaitGroup) {
    defer wg.Done()
    for job := range jobs {
        fmt.Printf("Worker %d started job %d\n", id, job)
        results <- job * 2
    }
}

func main() {
    const numJobs = 10
    const numWorkers = 3

    jobs := make(chan int, numJobs)
    results := make(chan int, numJobs)

    var wg sync.WaitGroup

    for w := 1; w <= numWorkers; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

    for j := 1; j <= numJobs; j++ {
        jobs <- j
    }
    close(jobs)

    wg.Wait()
    close(results)

    for result := range results {
        fmt.Println("Result:", result)
    }
}
```

---

## 二、Context 控制

```go
package main

import (
    "context"
    "fmt"
    "time"
)

func worker(ctx context.Context, id int) {
    for {
        select {
        case <-ctx.Done():
            fmt.Printf("Worker %d stopping: %v\n", id, ctx.Err())
            return
        default:
            fmt.Printf("Worker %d working...\n", id)
            time.Sleep(1 * time.Second)
        }
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    go worker(ctx, 1)
    go worker(ctx, 2)

    time.Sleep(3 * time.Second)
    cancel()
    time.Sleep(1 * time.Second)
}
```

---

## 三、超时控制

```go
package main

import (
    "context"
    "fmt"
    "time"
)

func slowOperation(ctx context.Context) error {
    select {
    case <-time.After(5 * time.Second):
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()

    err := slowOperation(ctx)
    if err != nil {
        fmt.Println("Operation failed:", err)
    } else {
        fmt.Println("Operation completed")
    }
}
```

---

## 四、Pipeline 模式

```go
package main

import "fmt"

func generator(nums ...int) <-chan int {
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

func filter(in <-chan int, threshold int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            if n > threshold {
                out <- n
            }
        }
        close(out)
    }()
    return out
}

func main() {
    c := generator(1, 2, 3, 4, 5)
    c = square(c)
    c = filter(c, 10)
    
    for n := range c {
        fmt.Println(n)
    }
}
```

---

## 五、扇出/扇入

```go
package main

import (
    "fmt"
    "sync"
)

func worker(id int, in <-chan int, out chan<- int, wg *sync.WaitGroup) {
    defer wg.Done()
    for n := range in {
        out <- n * 2
    }
}

func fanIn(cs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)

    for _, c := range cs {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for n := range c {
                out <- n
            }
        }(c)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}

func main() {
    in := make(chan int, 10)
    for i := 0; i < 10; i++ {
        in <- i
    }
    close(in)

    c1 := make(chan int)
    c2 := make(chan int)

    var wg sync.WaitGroup
    wg.Add(2)
    go worker(1, in, c1, &wg)
    go worker(2, in, c2, &wg)
    wg.Wait()
    close(c1)
    close(c2)

    merged := fanIn(c1, c2)
    for n := range merged {
        fmt.Println(n)
    }
}
```

---

## 六、限流与信号量

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

func worker(id int, sem chan struct{}, wg *sync.WaitGroup) {
    defer wg.Done()
    sem <- struct{}{}
    defer func() { <-sem }()

    fmt.Printf("Worker %d starting\n", id)
    time.Sleep(1 * time.Second)
    fmt.Printf("Worker %d done\n", id)
}

func main() {
    const limit = 2
    sem := make(chan struct{}, limit)
    var wg sync.WaitGroup

    for i := 0; i < 5; i++ {
        wg.Add(1)
        go worker(i, sem, &wg)
    }

    wg.Wait()
}
```

---

## 七、Mutex 与 RWMutex

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Counter struct {
    mu sync.RWMutex
    count int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *Counter) Get() int {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.count
}

func main() {
    c := &Counter{}

    for i := 0; i < 10; i++ {
        go func() {
            c.Inc()
        }()
    }

    time.Sleep(1 * time.Second)
    fmt.Println("Count:", c.Get())
}
```

---

## 八、Sync.Pool 对象池

```go
package main

import (
    "fmt"
    "sync"
)

type Buffer struct {
    data []byte
}

var pool = sync.Pool{
    New: func() interface{} {
        fmt.Println("Creating new buffer")
        return &Buffer{data: make([]byte, 1024)}
    },
}

func main() {
    buf1 := pool.Get().(*Buffer)
    fmt.Println("Using buf1")
    
    pool.Put(buf1)
    
    buf2 := pool.Get().(*Buffer)
    fmt.Println("Using buf2 (reused)")
}
```

---

## 九、Select 高级用法

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(1 * time.Second)
        ch1 <- "Hello"
    }()

    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "World"
    }()

    timeout := time.After(3 * time.Second)

    for i := 0; i < 3; i++ {
        select {
        case msg := <-ch1:
            fmt.Println("Received from ch1:", msg)
        case msg := <-ch2:
            fmt.Println("Received from ch2:", msg)
        case <-timeout:
            fmt.Println("Timeout!")
            return
        default:
            fmt.Println("No message ready")
            time.Sleep(500 * time.Millisecond)
        }
    }
}
```

---

## 十、ErrGroup

```go
package main

import (
    "fmt"
    "golang.org/x/sync/errgroup"
    "net/http"
)

func main() {
    g := new(errgroup.Group)
    urls := []string{
        "https://example.com",
        "https://example.org",
    }

    for _, url := range urls {
        url := url
        g.Go(func() error {
            resp, err := http.Get(url)
            if err != nil {
                return err
            }
            resp.Body.Close()
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("All requests successful")
    }
}
```

---

## 十一、最佳实践

1. 使用 Goroutine 池控制并发数
2. 使用 Context 管理生命周期
3. 使用 Pipeline 处理数据流
4. 使用 Semaphore 限流
5. 选择合适的同步原语（Mutex、RWMutex）

---

## 十二、总结

Go 提供了丰富的并发原语，合理使用能构建高性能的并发程序。
