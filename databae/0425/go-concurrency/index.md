# Go 并发编程深度解析：从 Goroutine 到 Channel

Go 的并发编程是其最强大的特性之一。本文将带你从基础到高级，全面掌握 Go 并发编程。

## 一、Goroutine

### 1. Goroutine 基础

```go
package main

import (
	"fmt"
	"time"
)

func sayHello() {
	fmt.Println("Hello from goroutine!")
}

func main() {
	go sayHello()  // 启动一个 goroutine
	
	fmt.Println("Hello from main!")
	
	time.Sleep(100 * time.Millisecond)  // 等待 goroutine 执行
}
```

### 2. 多个 Goroutine

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done()
	
	fmt.Printf("Worker %d starting\n", id)
	time.Sleep(time.Second)
	fmt.Printf("Worker %d done\n", id)
}

func main() {
	var wg sync.WaitGroup
	
	for i := 1; i <= 5; i++ {
		wg.Add(1)
		go worker(i, &wg)
	}
	
	wg.Wait()
	fmt.Println("All workers done")
}
```

## 二、Channel

### 1. 基础 Channel

```go
package main

import "fmt"

func main() {
	ch := make(chan string)
	
	go func() {
		ch <- "Hello from goroutine"
	}()
	
	message := <-ch
	fmt.Println(message)
}
```

### 2. 缓冲 Channel

```go
package main

import "fmt"

func main() {
	ch := make(chan int, 3)
	
	ch <- 1
	ch <- 2
	ch <- 3
	
	fmt.Println(<-ch)  // 1
	fmt.Println(<-ch)  // 2
	fmt.Println(<-ch)  // 3
}
```

### 3. 关闭 Channel

```go
package main

import "fmt"

func producer(ch chan<- int) {
	for i := 1; i <= 5; i++ {
		ch <- i
	}
	close(ch)
}

func main() {
	ch := make(chan int)
	
	go producer(ch)
	
	for num := range ch {
		fmt.Println(num)
	}
}
```

### 4. Select

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
		ch1 <- "one"
	}()
	
	go func() {
		time.Sleep(2 * time.Second)
		ch2 <- "two"
	}()
	
	for i := 0; i < 2; i++ {
		select {
		case msg1 := <-ch1:
			fmt.Println("Received", msg1)
		case msg2 := <-ch2:
			fmt.Println("Received", msg2)
		}
	}
}
```

## 三、同步原语

### 1. sync.WaitGroup

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	var wg sync.WaitGroup
	jobs := []string{"job1", "job2", "job3", "job4", "job5"}
	
	for _, job := range jobs {
		wg.Add(1)
		go func(j string) {
			defer wg.Done()
			fmt.Println("Processing", j)
			time.Sleep(time.Second)
		}(job)
	}
	
	wg.Wait()
	fmt.Println("All jobs completed")
}
```

### 2. sync.Mutex

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

type Counter struct {
	mu      sync.Mutex
	counter int
}

func (c *Counter) Increment() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.counter++
}

func (c *Counter) Value() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.counter
}

func main() {
	c := &Counter{}
	var wg sync.WaitGroup
	
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Increment()
		}()
	}
	
	wg.Wait()
	fmt.Println("Counter:", c.Value())
}
```

### 3. sync.RWMutex

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

type SafeMap struct {
	mu sync.RWMutex
	data map[string]string
}

func NewSafeMap() *SafeMap {
	return &SafeMap{
		data: make(map[string]string),
	}
}

func (sm *SafeMap) Get(key string) string {
	sm.mu.RLock()
	defer sm.mu.RUnlock()
	return sm.data[key]
}

func (sm *SafeMap) Set(key, value string) {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	sm.data[key] = value
}

func main() {
	sm := NewSafeMap()
	var wg sync.WaitGroup
	
	// 写操作
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key := fmt.Sprintf("key%d", i)
			sm.Set(key, fmt.Sprintf("value%d", i))
		}(i)
	}
	
	// 读操作
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			time.Sleep(10 * time.Millisecond)
			key := fmt.Sprintf("key%d", i%10)
			_ = sm.Get(key)
		}()
	}
	
	wg.Wait()
	fmt.Println("Done")
}
```

### 4. sync.Once

```go
package main

import (
	"fmt"
	"sync"
)

var (
	instance *Config
	once     sync.Once
)

type Config struct {
	Value string
}

func getConfig() *Config {
	once.Do(func() {
		fmt.Println("Initializing config")
		instance = &Config{Value: "initialized"}
	})
	return instance
}

func main() {
	var wg sync.WaitGroup
	
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			cfg := getConfig()
			fmt.Println(cfg.Value)
		}()
	}
	
	wg.Wait()
}
```

### 5. sync.Cond

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	var (
		mu      sync.Mutex
		cond    = sync.NewCond(&mu)
		ready   bool
		message string
	)
	
	waiter := func(id int) {
		mu.Lock()
		for !ready {
			cond.Wait()
		}
		fmt.Printf("Waiter %d received: %s\n", id, message)
		mu.Unlock()
	}
	
	for i := 1; i <= 3; i++ {
		go waiter(i)
	}
	
	time.Sleep(1 * time.Second)
	
	mu.Lock()
	ready = true
	message = "Hello!"
	cond.Broadcast()
	mu.Unlock()
	
	time.Sleep(1 * time.Second)
}
```

## 四、Context

### 1. 基础 Context

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
			fmt.Printf("Worker %d: %v\n", id, ctx.Err())
			return
		default:
			fmt.Printf("Worker %d working\n", id)
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
	cancel()
	time.Sleep(500 * time.Millisecond)
}
```

### 2. Context WithTimeout

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
		fmt.Println("Operation completed")
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
		fmt.Println("Error:", err)
	}
}
```

### 3. Context WithValue

```go
package main

import (
	"context"
	"fmt"
)

type contextKey string

const userIDKey contextKey = "userID"

func doSomething(ctx context.Context) {
	userID := ctx.Value(userIDKey).(string)
	fmt.Println("User ID:", userID)
}

func main() {
	ctx := context.WithValue(context.Background(), userIDKey, "123")
	doSomething(ctx)
}
```

## 五、工作池模式

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

type Job struct {
	ID  int
	Data string
}

type Result struct {
	JobID int
	Output string
}

func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	
	for job := range jobs {
		fmt.Printf("Worker %d processing job %d\n", id, job.ID)
		time.Sleep(500 * time.Millisecond)
		
		results <- Result{
			JobID: job.ID,
			Output: fmt.Sprintf("Processed: %s", job.Data),
		}
	}
}

func main() {
	const numJobs = 10
	const numWorkers = 3
	
	jobs := make(chan Job, numJobs)
	results := make(chan Result, numJobs)
	
	var wg sync.WaitGroup
	
	for w := 1; w <= numWorkers; w++ {
		wg.Add(1)
		go worker(w, jobs, results, &wg)
	}
	
	for j := 1; j <= numJobs; j++ {
		jobs <- Job{ID: j, Data: fmt.Sprintf("data%d", j)}
	}
	close(jobs)
	
	go func() {
		wg.Wait()
		close(results)
	}()
	
	for result := range results {
		fmt.Printf("Result: job %d, %s\n", result.JobID, result.Output)
	}
}
```

## 六、最佳实践

1. 优先使用 Channel 而非共享内存
2. 使用 Goroutine 处理并发任务
3. 正确使用 WaitGroup 等待任务完成
4. 使用 Mutex 保护共享资源
5. 使用 Context 控制超时和取消
6. 避免 Goroutine 泄漏
7. 使用工作池模式限制并发数
8. 正确关闭 Channel
9. 使用 Select 处理多路复用
10. 避免在 Goroutine 中使用全局变量

## 七、总结

Go 并发编程核心要点：
- Goroutine 轻量级线程
- Channel 用于通信
- sync 包同步原语（WaitGroup、Mutex、RWMutex、Once、Cond）
- Context 控制超时和取消
- 工作池模式
- 最佳实践

开始用 Go 构建高性能并发应用吧！
