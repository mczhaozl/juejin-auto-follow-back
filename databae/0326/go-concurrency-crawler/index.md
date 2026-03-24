# Go 语言入门：从零开始构建一个高性能的并发 Web 爬虫

> Go 语言天生适合高并发任务。本文将带你利用 Goroutine 和 Channel，从零开始实现一个高性能的 Web 爬虫，并学习如何优雅地处理并发限制与任务调度。

## 一、为什么选择 Go 来写爬虫？

在爬取成千上万个页面时，**并发能力**是关键。

- **Goroutine**: 极轻量级的线程（通常只需几 KB 内存），单机支持数百万个并发。
- **Channel**: 通过消息通信来共享内存（Don't communicate by sharing memory; share memory by communicating），让并发代码更安全、更易理解。
- **标准库**: 拥有非常强大的 `net/http`。

## 二、基础版：顺序爬虫

```go
func crawl(url string) {
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	defer resp.Body.Close()
	fmt.Printf("Crawled %s, Status: %s\n", url, resp.Status)
}
```

## 三、进阶版：并发爬虫 (Goroutine)

如果直接循环开启 Goroutine：
```go
for _, url := range urls {
	go crawl(url)
}
```
**问题：** 可能会瞬间开启成千上万个请求，导致被目标服务器封禁或本地资源耗尽。

## 四、高手版：并发限制 (Worker Pool)

利用 **Channel** 实现一个 Worker Pool，精确控制并发数量。

```go
func worker(id int, jobs <-chan string, results chan<- string) {
	for url := range jobs {
		fmt.Printf("Worker %d starting job %s\n", id, url)
		crawl(url)
		results <- url + " done"
	}
}

func main() {
	jobs := make(chan string, 100)
	results := make(chan string, 100)

	// 1. 开启 5 个并发 Worker
	for w := 1; w <= 5; w++ {
		go worker(w, jobs, results)
	}

	// 2. 发送任务
	for _, url := range urls {
		jobs <- url
	}
	close(jobs) // 发送完毕

	// 3. 收集结果
	for a := 1; a <= len(urls); a++ {
		<-results
	}
}
```

## 五、处理并发安全：Sync.WaitGroup

在实际项目中，我们通常配合 `sync.WaitGroup` 来等待所有任务完成。

```go
var wg sync.WaitGroup
for _, url := range urls {
	wg.Add(1)
	go func(u string) {
		defer wg.Done()
		crawl(u)
	}(url)
}
wg.Wait()
```

## 六、总结

Go 的并发模型（CSP 模型）让高并发编程变得平民化。通过 Channel 和 Goroutine 的配合，我们可以非常简单地构建出高性能的后端服务。

**你是否在项目中使用过 Go 的并发特性？欢迎分享你的实战技巧！**
