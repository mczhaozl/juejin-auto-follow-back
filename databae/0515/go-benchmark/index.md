# Go 基准测试完全指南

## 一、基础 Benchmark

```go
package main

import "testing"

func BenchmarkSum(b *testing.B) {
  for i := 0; i < b.N; i++ {
    Sum(1000)
  }
}
```

## 二、运行

```bash
go test -bench . -benchmem
```

## 三、ResetTimer

```go
func BenchmarkInit(b *testing.B) {
  // 准备
  heavySetup()
  b.ResetTimer()
  
  for i := 0; i < b.N; i++ {
    // 测试代码
  }
}
```

## 四、pprof

```bash
go test -bench . -cpuprofile cpu.pprof
go tool pprof cpu.pprof
```

## 最佳实践
- 基准测试真实场景
- 多次运行取平均值
- 使用 -benchmem 看内存
- ResetTimer 避免准备耗时
- 对比优化前后
