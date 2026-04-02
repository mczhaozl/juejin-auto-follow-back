# Node.js Streams 完全指南：深入理解流式处理

> 一句话摘要：全面解析 Node.js Streams，涵盖可读流、可写流、转换流的原理与实践，学习如何使用流处理大文件、构建高效的数据管道，提升 Node.js 应用的性能和内存效率。

## 一、流的概念与重要性

### 1.1 什么是流

流（Stream）是 Node.js 中处理数据的一种抽象方式。它不是一次性读取所有数据，而是**数据流经一系列处理阶段**，每个阶段对数据进行操作。

```
┌─────────────────────────────────────────────────────────────────┐
│                         Stream 示意图                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   数据源 ──→ Chunk 1 ──→ Chunk 2 ──→ Chunk 3 ──→ ... ──→ 数据汇 │
│                                                                  │
│   [Readable]      [Transform]    [Transform]      [Writable]   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 为什么使用流

传统方式 vs 流方式：

```javascript
// ❌ 传统方式：一次性加载整个文件到内存
const fs = require('fs');

function copyFileTraditional(src, dest) {
    // 读取整个文件到内存
    const data = fs.readFileSync(src);

    // 写入整个文件
    fs.writeFileSync(dest, data);

    // 问题：对于大文件（如 4K 视频），会占用大量内存
    // 1GB 文件就需要 1GB+ 内存
}

// ✅ 流方式：分块处理，内存占用恒定
function copyFileStream(src, dest) {
    const readStream = fs.createReadStream(src);
    const writeStream = fs.createWriteStream(dest);

    readStream.pipe(writeStream);
    // 无论文件多大，内存占用都很小
}
```

### 1.3 流的应用场景

| 场景 | 传统方式问题 | 流方式优势 |
|------|-------------|-----------|
| 大文件复制 | 内存爆炸 | 内存占用恒定 |
| 文件压缩/解压 | 需要完整文件 | 边读边压缩 |
| HTTP 大文件上传 | 内存溢出 | 流式处理 |
| 日志处理 | 内存不足 | 增量处理 |
| 数据转换 | 全量加载 | 实时转换 |

## 二、流的四种类型

### 2.1 可读流（Readable Streams）

```javascript
const { Readable } = require('stream');

// 创建自定义可读流
class CounterStream extends Readable {
    constructor(max = 100) {
        super();
        this.max = max;
        this.current = 0;
    }

    // 必须实现 _read 方法
    _read() {
        if (this.current > this.max) {
            // 返回 null 表示流结束
            this.push(null);
        } else {
            // push 一个数字
            const chunk = Buffer.from(String(this.current++));
            this.push(chunk);
        }
    }
}

// 使用
const counter = new CounterStream(10);

counter.on('data', (chunk) => {
    console.log('收到数据:', chunk.toString());
});

counter.on('end', () => {
    console.log('流已结束');
});
```

### 2.2 可写流（Writable Streams）

```javascript
const { Writable } = require('stream');

// 创建自定义可写流
class UpperCaseWriter extends Writable {
    constructor(options) {
        super(options);
        this.chunks = [];
    }

    // 必须实现 _write 方法
    _write(chunk, encoding, callback) {
        // chunk 是 Buffer
        const upperCased = chunk.toString().toUpperCase();
        this.chunks.push(upperCased);
        console.log('写入:', upperCased);

        // 调用 callback 表示这块数据已处理完成
        callback();
    }

    // 可选：实现 _final 方法，在流关闭前做最后的处理
    _final(callback) {
        console.log('所有数据已写入完毕');
        console.log('结果:', this.chunks.join(''));
        callback();
    }
}

// 使用
const writer = new UpperCaseWriter();

writer.write(Buffer.from('hello '));
writer.write(Buffer.from('world '));
writer.write(Buffer.from('!!!'));
writer.end(); // 标记写入结束
```

### 2.3 转换流（Transform Streams）

```javascript
const { Transform } = require('stream');

// 创建转换流：JSON 解析
class JSONParser extends Transform {
    constructor() {
        super({ objectMode: true }); // objectMode 允许输出对象而非 Buffer
        this.buffer = '';
    }

    _transform(chunk, encoding, callback) {
        this.buffer += chunk.toString();

        // 尝试解析完整的 JSON 对象
        try {
            const parsed = JSON.parse(this.buffer);
            this.push(parsed);
            this.buffer = '';
        } catch (e) {
            // 数据不完整，等待更多数据
            // 不调用 callback，继续累积
        }

        callback();
    }

    _flush(callback) {
        // 处理残留数据
        if (this.buffer.trim()) {
            try {
                const parsed = JSON.parse(this.buffer);
                this.push(parsed);
            } catch (e) {
                this.emit('error', new Error('Invalid JSON'));
            }
        }
        callback();
    }
}

// 使用
const parser = new JSONParser();

parser.on('data', (obj) => {
    console.log('解析对象:', obj);
});

parser.write(Buffer.from('{"name":"张三"}'));
parser.write(Buffer.from(',{"age":25}'));
parser.end();
```

### 2.4 双工流（Duplex Streams）

```javascript
const { Duplex } = require('stream');

// 双工流：同时可读可写
class EchoDuplex extends Duplex {
    constructor(options) {
        super(options);
        this.buffer = [];
    }

    // 可读端
    _read(size) {
        if (this.buffer.length) {
            const chunk = this.buffer.shift();
            this.push(chunk);
        } else {
            // 如果没有数据，稍后重试
            setTimeout(() => this._read(size), 100);
        }
    }

    // 可写端
    _write(chunk, encoding, callback) {
        console.log('收到写入:', chunk.toString());
        this.buffer.push(chunk);
        callback();
    }
}

const echo = new EchoDuplex();

// 写入数据
echo.write(Buffer.from('Hello'));

// 读取数据
echo.on('data', (chunk) => {
    console.log('读取数据:', chunk.toString());
});
```

## 三、流的核心方法

### 3.1 pipe 方法

```javascript
const { createReadStream, createWriteStream } = require('fs');
const { createGzip } = require('zlib');

// 经典用法：文件压缩
createReadStream('input.txt')
    .pipe(createGzip())                    // 转换流
    .pipe(createWriteStream('output.txt.gz'));  // 可写流

// pipe 返回目标流，可以链式调用
readStream
    .pipe(transform1())
    .pipe(transform2())
    .pipe(writeStream);
```

### 3.2 背压（Backpressure）

当写入速度跟不上读取速度时，需要处理背压：

```javascript
// 没有背压处理 - 可能导致内存溢出
readStream.on('data', (chunk) => {
    const result = process(chunk);
    writeStream.write(result);  // 写入可能失败
});

// 正确处理背压
readStream.on('data', (chunk) => {
    const result = process(chunk);
    const canContinue = writeStream.write(result);

    // 如果返回 false，说明写入缓冲区已满
    if (!canContinue) {
        // 暂停读取，等待 drain 事件
        readStream.pause();

        // 当缓冲区清空时，恢复读取
        writeStream.once('drain', () => {
            readStream.resume();
        });
    }
});
```

### 3.3 异步迭代器支持

```javascript
const { forEach } = require('util').promisify;

// Node.js 10+ 支持 for await...of
async function processStream(readable) {
    for await (const chunk of readable) {
        console.log('处理数据块:', chunk.toString());
    }
    console.log('处理完成');
}

// 转换为异步迭代器
const readable = getReadableStream();
readable[Symbol.asyncIterator]();
```

### 3.4 Stream 事件

```javascript
const { Readable } = require('stream');

const readable = new Readable({
    read(size) {
        // 当需要更多数据时调用
        const data = fetchData();
        if (data) {
            this.push(data);
        } else {
            this.push(null); // 结束流
        }
    }
});

// 常用事件
readable.on('data', (chunk) => { /* 处理数据 */ });
readable.on('end', () => { /* 流结束 */ });
readable.on('error', (err) => { /* 错误处理 */ });
readable.on('close', () => { /* 流关闭 */ });
readable.on('readable', () => { /* 数据可读（flowing 模式） */ });
```

## 四、实用案例

### 4.1 大文件处理

```javascript
const fs = require('fs');
const { createReadStream, createWriteStream } = fs;
const { pipeline } = require('stream').promises;

// 案例 1：复制大文件
async function copyBigFile(src, dest, highWaterMark = 64 * 1024) {
    const readStream = createReadStream(src, {
        highWaterMark  // 默认 64KB，可调整
    });
    const writeStream = createWriteStream(dest);

    await pipeline(readStream, writeStream);

    console.log(`文件已复制: ${src} -> ${dest}`);
}

// 案例 2：CSV 文件处理
const { parse } = require('csv-parse');

async function processLargeCSV(filePath) {
    const parser = parse({
        columns: true,       // 第一行作为列名
        skip_empty_lines: true,
        cast: true           // 自动转换类型
    });

    const readStream = createReadStream(filePath);

    let rowCount = 0;
    let sum = 0;

    await pipeline(
        readStream,
        parser,
        new Transform({
            objectMode: true,
            transform(row, encoding, callback) {
                rowCount++;
                sum += row.amount || 0;

                if (rowCount % 10000 === 0) {
                    console.log(`已处理 ${rowCount} 行`);
                }

                callback();
            }
        })
    );

    console.log(`总行数: ${rowCount}, 总金额: ${sum}`);
}

// 案例 3：文件压缩
const { createGzip, createGunzip } = require('zlib');
const { promisify } = require('util');
const pipelineAsync = promisify pipeline;

async function compressFile(src, dest) {
    await pipelineAsync(
        createReadStream(src),
        createGzip(),
        createWriteStream(dest)
    );
}

async function decompressFile(src, dest) {
    await pipelineAsync(
        createReadStream(src),
        createGunzip(),
        createWriteStream(dest)
    );
}
```

### 4.2 HTTP 流处理

```javascript
const http = require('http');
const { createReadStream } = require('fs');

// 案例 1：流式响应大文件
const server = http.createServer((req, res) => {
    const filePath = './large-file.zip';

    // 设置 headers
    res.writeHead(200, {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': 'attachment; filename="large-file.zip"',
        'Transfer-Encoding': 'chunked'
    });

    const readStream = createReadStream(filePath);

    // 处理错误
    readStream.on('error', (err) => {
        console.error('文件读取错误:', err);
        res.end('文件读取失败');
    });

    // 流式传输
    readStream.pipe(res);
});

// 案例 2：流式接收上传文件
const server2 = http.createServer((req, res) => {
    if (req.url === '/upload' && req.method === 'POST') {
        const writeStream = createWriteStream('./uploads/file.zip');
        let uploadSize = 0;

        req.on('data', (chunk) => {
            uploadSize += chunk.length;
            console.log(`已上传: ${uploadSize} bytes`);
        });

        req.pipe(writeStream);

        writeStream.on('finish', () => {
            res.end('上传成功');
        });

        req.on('error', (err) => {
            console.error('上传错误:', err);
            writeStream.destroy();
            res.end('上传失败');
        });
    }
});

// 案例 3：代理服务器
const proxyServer = http.createServer((req, res) => {
    const options = {
        hostname: 'example.com',
        port: 80,
        path: req.url,
        method: req.method,
        headers: req.headers
    };

    const proxyReq = http.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
    });

    req.pipe(proxyReq);

    req.on('error', (err) => {
        console.error('请求错误:', err);
        res.end('代理错误');
    });
});
```

### 4.3 数据转换

```javascript
const { Transform, pipeline } = require('stream');
const { createReadStream, createWriteStream } = require('fs');
const { promisify } = require('util');

// 案例 1：行转换器
class LineTransformer extends Transform {
    constructor(options) {
        super(options);
        this.currentLine = '';
    }

    _transform(chunk, encoding, callback) {
        const text = this.currentLine + chunk.toString();
        const lines = text.split('\n');

        // 保留最后一行（可能不完整）
        this.currentLine = lines.pop();

        // 输出所有完整行
        for (const line of lines) {
            this.push(line + '\n');
        }

        callback();
    }

    _flush(callback) {
        // 处理最后一行
        if (this.currentLine) {
            this.push(this.currentLine);
        }
        callback();
    }
}

// 案例 2：数据统计
class DataStatistics extends Transform {
    constructor(options) {
        super({ objectMode: true });
        this.count = 0;
        this.sum = 0;
        this.min = Infinity;
        this.max = -Infinity;
    }

    _transform(record, encoding, callback) {
        this.count++;
        const value = typeof record === 'object' ? record.value : record;

        if (typeof value === 'number') {
            this.sum += value;
            this.min = Math.min(this.min, value);
            this.max = Math.max(this.max, value);
        }

        callback();
    }

    _flush(callback) {
        this.push({
            count: this.count,
            sum: this.sum,
            avg: this.count > 0 ? this.sum / this.count : 0,
            min: this.min,
            max: this.max
        });
        callback();
    }
}

// 案例 3：加密转换
const crypto = require('crypto');

class CryptoTransform extends Transform {
    constructor(algorithm, key) {
        super();
        this.algorithm = algorithm;
        this.key = key;
    }

    _transform(chunk, encoding, callback) {
        const cipher = crypto.createCipher(this.algorithm, this.key);
        const encrypted = Buffer.concat([
            cipher.update(chunk),
            cipher.final()
        ]);
        this.push(encrypted);
        callback();
    }
}
```

### 4.4 WebSocket 与流

```javascript
const WebSocket = require('ws');
const { createReadStream } = require('fs');

// WebSocket 服务器
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
    console.log('客户端连接');

    // 读取文件并发送给客户端
    const readStream = createReadStream('./large-data.json');

    readStream.on('data', (chunk) => {
        // 检查客户端是否准备好接收
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(chunk);
        }
    });

    readStream.on('end', () => {
        ws.send(JSON.stringify({ type: 'end' }));
    });

    ws.on('message', (message) => {
        console.log('收到消息:', message.toString());
    });

    ws.on('close', () => {
        console.log('客户端断开');
        readStream.destroy();
    });
});
```

## 五、性能优化

### 5.1 highWaterMark 设置

```javascript
// highWaterMark 控制内部缓冲区大小

// 低值：内存占用低，但频繁调用 _read
const lowWaterMark = createReadStream('./file', {
    highWaterMark: 1024  // 1KB
});

// 高值：内存占用高，但减少调用次数
const highWaterMark = createReadStream('./file', {
    highWaterMark: 1024 * 1024  // 1MB
});

// 对于网络流，通常使用默认值或稍高
const httpStream = fetch(url, {
    highWaterMark: 64 * 1024  // 64KB
});
```

### 5.2 并行流处理

```javascript
const { Transform, pipeline } = require('stream');
const { createReadStream, createWriteStream } = require('fs');

// 并行处理：使用 worker pool
class ParallelTransform extends Transform {
    constructor(parallel = 4) {
        super({ objectMode: true });
        this.parallel = parallel;
        this.running = 0;
        this.queue = [];
    }

    async _transform(item, encoding, callback) {
        this.running++;
        this.queue.push({ item, callback });

        if (this.running < this.parallel) {
            this.processQueue();
        } else {
            // 等待槽位空闲
        }
    }

    async processQueue() {
        while (this.queue.length > 0 && this.running < this.parallel) {
            const { item, callback } = this.queue.shift();
            this.running++;

            try {
                const result = await processItem(item);
                this.push(result);
            } catch (err) {
                this.emit('error', err);
            }

            this.running--;
            callback();

            // 继续处理队列
            if (this.queue.length > 0 && this.running < this.parallel) {
                setImmediate(() => this.processQueue());
            }
        }
    }

    _flush(callback) {
        // 等待所有处理完成
        const checkDone = () => {
            if (this.running === 0) {
                callback();
            } else {
                setImmediate(checkDone);
            }
        };
        checkDone();
    }
}
```

### 5.3 内存管理

```javascript
// 优化内存使用

// 1. 对象模式 vs Buffer 模式
const bufferStream = createReadStream('./data');  // 输出 Buffer
bufferStream.on('data', (chunk) => {
    console.log(typeof chunk);  // 'object' (Buffer)
});

// 对象模式：减少内存拷贝
const objectStream = createReadStream('./data', {
    objectMode: true,
    encoding: 'utf8'
});
objectStream.on('data', (chunk) => {
    console.log(typeof chunk);  // 'string'
});

// 2. 及时销毁流
function processFile(filePath) {
    const stream = createReadStream(filePath);

    stream.on('data', (chunk) => {
        // 处理...
    });

    stream.on('end', () => {
        stream.destroy();  // 确保释放资源
    });

    stream.on('error', (err) => {
        stream.destroy();  // 出错时也要销毁
    });

    return stream;
}

// 3. 使用 pause/resume 控制流速
class ControlledStream extends Readable {
    _read(size) {
        if (this.shouldPause) {
            setTimeout(() => {
                this.shouldPause = false;
                this._read(size);
            }, 100);
        } else {
            // 正常读取
            const data = fetchData();
            if (data) {
                this.push(data);
            } else {
                this.push(null);
            }
        }
    }
}
```

### 5.4 错误处理

```javascript
const { pipeline } = require('stream').promises;
const { createReadStream, createWriteStream } = require('fs');

// 推荐：使用 pipeline 自动处理错误和清理
async function processWithPipeline() {
    try {
        await pipeline(
            createReadStream('input.txt'),
            new UppercaseTransform(),
            new FilterTransform(),
            createWriteStream('output.txt')
        );
        console.log('处理完成');
    } catch (err) {
        console.error('处理失败:', err);
        // pipeline 会自动销毁所有流
    }
}

// 传统方式：手动错误处理
function processManual() {
    const readStream = createReadStream('input.txt');
    const writeStream = createWriteStream('output.txt');

    readStream.on('error', (err) => {
        console.error('读取错误:', err);
        writeStream.destroy();
    });

    writeStream.on('error', (err) => {
        console.error('写入错误:', err);
        readStream.destroy();
    });

    readStream.pipe(writeStream);

    writeStream.on('finish', () => {
        console.log('写入完成');
    });
}
```

## 六、流的模式

### 6.1 Flowing 模式

```javascript
// Flowing 模式：自动读取数据，需要消费
const readStream = createReadStream('./file.txt');

readStream.on('data', (chunk) => {
    console.log('收到数据:', chunk.toString());
});

readStream.on('end', () => {
    console.log('流结束');
});
```

### 6.2 Paused 模式

```javascript
// Paused 模式：手动读取数据
const readStream = createReadStream('./file.txt', {
    encoding: 'utf8'
});

readStream.on('readable', () => {
    // 手动调用 read() 读取数据
    let chunk;
    while ((chunk = readStream.read()) !== null) {
        console.log('读取数据:', chunk);
    }
});

readStream.on('end', () => {
    console.log('流结束');
});

// 切换模式
readStream.pause();   // 暂停读取
readStream.resume(); // 恢复读取
```

## 七、常见问题与解决方案

### 7.1 流未正确关闭

```javascript
// 问题：流未正确关闭导致文件被锁
const stream = createReadStream('./file');
stream.pipe(someTransform);

// 解决方案：监听事件正确关闭
const { pipeline } = require('stream').promises;

await pipeline(
    createReadStream('./file'),
    someTransform,
    createWriteStream('./output')
);
// pipeline 会自动处理流关闭
```

### 7.2 内存泄漏

```javascript
// 问题：未消费的流导致内存泄漏
const stream = createReadStream('./huge-file');
stream.on('data', (chunk) => {
    if (someCondition) {
        stream.destroy();  // 提前销毁
    }
});

// 解决方案：确保消费完所有数据
const { finished } = require('stream');

finished(stream, (err) => {
    if (err) {
        console.error('流错误:', err);
    } else {
        console.log('流已结束');
    }
});
```

### 7.3 管道断裂

```javascript
// 问题：写入目标出错导致管道断裂
readStream
    .pipe(transform1())
    .pipe(transform2())
    .pipe(writeStream);

// 写入出错时，不会自动传播到读取流

// 解决方案：使用 pipeline
const { pipeline } = require('stream').promises;

await pipeline(
    readStream,
    transform1(),
    transform2(),
    writeStream
);
// pipeline 会正确处理所有流的销毁
```

## 八、实用工具函数

### 8.1 readable-webify

```javascript
// 将 Web API ReadableStream 转换为 Node.js 流
const { Readable } = require('stream');

function fromWebReadable(webReadable) {
    return Readable.fromWeb(webReadable);
}

// 使用
const response = await fetch('https://api.example.com/data');
const nodeReadable = Readable.fromWeb(response.body);
```

### 8.2 compose

```javascript
// 组合多个流
const { compose } = require('stream');

const transform = compose(
    new Transform1(),
    new Transform2(),
    new Transform3()
);

readStream.pipe(transform).pipe(writeStream);
```

### 8.3 PassThrough

```javascript
const { PassThrough } = require('stream');

// 不做任何转换，直接传递数据
// 常用于调试或分支流
const pass = new PassThrough();

readStream
    .pipe(transform1())
    .pipe(pass)  // 分支点
    .pipe(writeStream1());

pass
    .pipe(transform2())
    .pipe(writeStream2());
```

## 九、总结

### 9.1 核心要点

1. **Node.js Streams 是处理数据的一种高效方式**
2. **四种类型：Readable、Writable、Transform、Duplex**
3. **pipe 方法连接流，pipeline 处理错误和清理**
4. **注意背压处理，避免内存问题**
5. **使用 highWaterMark 调整缓冲区大小**

### 9.2 最佳实践

- ✅ 使用 `pipeline` 替代 `pipe` 进行错误处理
- ✅ 处理背压，避免内存溢出
- ✅ 设置合适的 `highWaterMark`
- ✅ 使用对象模式减少类型转换
- ❌ 不要忘记调用 `callback()` 或 `push(null)`
- ❌ 不要在 `_transform` 中同步调用 callback

### 9.3 性能对比

| 场景 | 传统方式 | 流方式 |
|------|---------|--------|
| 1GB 文件复制 | 1GB+ 内存 | ~1MB 内存 |
| HTTP 响应 | 阻塞 | 流式 |
| CSV 处理 | 全量解析 | 增量处理 |

> 如果对你有帮助，欢迎点赞、收藏！有任何问题欢迎在评论区讨论。
