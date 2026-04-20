# Go sync.Pool 完全指南

## 一、基础 Pool

```go
package main

import (
  "sync"
)

type Buffer struct {
  Data []byte
}

var bufPool = sync.Pool{
  New: func() interface{} {
    return &Buffer{
      Data: make([]byte, 1024),
    }
  },
}

func main() {
  // 获取对象
  buf := bufPool.Get().(*Buffer)
  buf.Data = append(buf.Data, "Hello"...)
  
  // 使用...
  
  // 重置并放回
  buf.Data = buf.Data[:0]
  bufPool.Put(buf)
}
```

## 二、json.Encoder 池

```go
import (
  "encoding/json"
  "io"
  "sync"
)

var encoderPool = sync.Pool{
  New: func() interface{} {
    return json.NewEncoder(nil)
  },
}

func WriteJSON(w io.Writer, v interface{}) error {
  enc := encoderPool.Get().(*json.Encoder)
  defer encoderPool.Put(enc)
  
  enc.Reset(w)
  return enc.Encode(v)
}
```

## 三、bytes.Buffer 池

```go
import (
  "bytes"
  "sync"
)

var bufferPool = sync.Pool{
  New: func() interface{} {
    return new(bytes.Buffer)
  },
}

func GetBuffer() *bytes.Buffer {
  return bufferPool.Get().(*bytes.Buffer)
}

func PutBuffer(buf *bytes.Buffer) {
  buf.Reset()
  bufferPool.Put(buf)
}
```

## 四、Pool 的注意事项

```go
// 1. Pool 可能被 GC 清理
// 2. Pool 中对象是临时的
// 3. 对象必须重置干净
// 4. 适合高并发重复使用的对象
```

## 最佳实践
- 对象需要频繁创建销毁
- 正确重置对象状态
- 不要假设 Pool 会保留对象
- 注意 Pool 的大小和 GC 压力
- 性能分析后再决定使用
