# Node.js 文件系统与流处理完全指南：从基础到高性能

Node.js 的 fs 模块和流处理是构建高性能应用的关键。本文将带你全面掌握这些内容。

## 一、fs 模块基础

### 1. 同步 vs 异步

```javascript
const fs = require('fs');

// 同步读取
try {
  const data = fs.readFileSync('file.txt', 'utf8');
  console.log(data);
} catch (err) {
  console.error(err);
}

// 异步读取（回调）
fs.readFile('file.txt', 'utf8', (err, data) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log(data);
});

// 异步读取（Promise）
const fsPromises = require('fs').promises;

async function readFileAsync() {
  try {
    const data = await fsPromises.readFile('file.txt', 'utf8');
    console.log(data);
  } catch (err) {
    console.error(err);
  }
}
```

### 2. 常用文件操作

```javascript
const fs = require('fs');
const path = require('path');

// 读取文件
fs.readFile('file.txt', 'utf8', (err, data) => {});

// 写入文件
fs.writeFile('file.txt', 'Hello World', (err) => {});

// 追加文件
fs.appendFile('file.txt', 'More content', (err) => {});

// 删除文件
fs.unlink('file.txt', (err) => {});

// 重命名文件
fs.rename('old.txt', 'new.txt', (err) => {});

// 检查文件是否存在
fs.access('file.txt', fs.constants.F_OK, (err) => {
  if (err) {
    console.log('文件不存在');
  } else {
    console.log('文件存在');
  }
});

// 获取文件信息
fs.stat('file.txt', (err, stats) => {
  if (err) throw err;
  console.log(stats.isFile());
  console.log(stats.isDirectory());
  console.log(stats.size);
  console.log(stats.mtime);
});
```

### 3. 目录操作

```javascript
// 创建目录
fs.mkdir('mydir', { recursive: true }, (err) => {});

// 读取目录
fs.readdir('mydir', (err, files) => {
  if (err) throw err;
  console.log(files);
});

// 读取目录（带详细信息）
fs.readdir('mydir', { withFileTypes: true }, (err, files) => {
  if (err) throw err;
  files.forEach(file => {
    console.log(file.name, file.isDirectory());
  });
});

// 删除目录
fs.rmdir('mydir', { recursive: true }, (err) => {});
```

## 二、流处理基础

### 1. 为什么用流

```javascript
// ❌ 不好：一次性读取大文件
const data = fs.readFileSync('large-file.txt'); // 内存爆炸！

// ✅ 好：使用流处理
const stream = fs.createReadStream('large-file.txt');
stream.on('data', (chunk) => {
  console.log(`Received ${chunk.length} bytes of data.`);
});
```

### 2. 可读流

```javascript
const readStream = fs.createReadStream('file.txt', {
  encoding: 'utf8',
  highWaterMark: 64 * 1024 // 64KB
});

readStream.on('data', (chunk) => {
  console.log('Chunk:', chunk);
});

readStream.on('end', () => {
  console.log('Reading finished');
});

readStream.on('error', (err) => {
  console.error('Error:', err);
});

readStream.on('open', () => {
  console.log('File opened');
});
```

### 3. 可写流

```javascript
const writeStream = fs.createWriteStream('output.txt');

writeStream.write('Hello\n');
writeStream.write('World\n');
writeStream.end('Done\n');

writeStream.on('finish', () => {
  console.log('Writing finished');
});

writeStream.on('error', (err) => {
  console.error('Error:', err);
});
```

### 4. 管道 (pipe)

```javascript
// 复制文件
const readStream = fs.createReadStream('input.txt');
const writeStream = fs.createWriteStream('output.txt');

readStream.pipe(writeStream);

// 链式管道
const zlib = require('zlib');
fs.createReadStream('file.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('file.txt.gz'));
```

## 三、流的类型

### 1. Readable（可读流）

```javascript
const { Readable } = require('stream');

class CounterStream extends Readable {
  constructor(options) {
    super(options);
    this._max = 10;
    this._index = 0;
  }

  _read(size) {
    if (this._index++ < this._max) {
      this.push(`${this._index}\n`);
    } else {
      this.push(null);
    }
  }
}

const counter = new CounterStream();
counter.pipe(process.stdout);
```

### 2. Writable（可写流）

```javascript
const { Writable } = require('stream');

class UpperCaseWriter extends Writable {
  constructor(options) {
    super(options);
  }

  _write(chunk, encoding, callback) {
    console.log(chunk.toString().toUpperCase());
    callback();
  }
}

const writer = new UpperCaseWriter();
writer.write('hello\n');
writer.write('world\n');
writer.end();
```

### 3. Duplex（双工流）

```javascript
const { Duplex } = require('stream');

class EchoStream extends Duplex {
  constructor(options) {
    super(options);
  }

  _read(size) {}

  _write(chunk, encoding, callback) {
    this.push(chunk);
    callback();
  }
}

const echo = new EchoStream();
echo.pipe(process.stdout);
echo.write('Hello\n');
```

### 4. Transform（转换流）

```javascript
const { Transform } = require('stream');

class UpperCaseTransform extends Transform {
  constructor(options) {
    super(options);
  }

  _transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  }
}

const upper = new UpperCaseTransform();
process.stdin.pipe(upper).pipe(process.stdout);
```

## 四、实战案例

### 1. 大文件复制

```javascript
const fs = require('fs');
const path = require('path');

function copyFile(src, dest) {
  return new Promise((resolve, reject) => {
    const readStream = fs.createReadStream(src);
    const writeStream = fs.createWriteStream(dest);

    readStream.on('error', reject);
    writeStream.on('error', reject);
    writeStream.on('finish', resolve);

    readStream.pipe(writeStream);
  });
}

async function main() {
  try {
    await copyFile('large-file.txt', 'large-file-copy.txt');
    console.log('Copy completed');
  } catch (err) {
    console.error('Copy failed:', err);
  }
}
```

### 2. 日志文件分析

```javascript
const fs = require('fs');
const readline = require('readline');

async function analyzeLogs(filePath) {
  const stats = {
    total: 0,
    errors: 0,
    warnings: 0
  };

  const rl = readline.createInterface({
    input: fs.createReadStream(filePath),
    crlfDelay: Infinity
  });

  for await (const line of rl) {
    stats.total++;
    if (line.includes('ERROR')) {
      stats.errors++;
    } else if (line.includes('WARN')) {
      stats.warnings++;
    }
  }

  return stats;
}
```

### 3. CSV 处理

```javascript
const fs = require('fs');
const { Transform } = require('stream');

class CSVParser extends Transform {
  constructor(options) {
    super({ ...options, readableObjectMode: true });
    this.headers = null;
  }

  _transform(chunk, encoding, callback) {
    const lines = chunk.toString().split('\n');
    
    if (!this.headers) {
      this.headers = lines.shift().split(',');
    }

    for (const line of lines) {
      if (line.trim()) {
        const values = line.split(',');
        const obj = {};
        this.headers.forEach((header, i) => {
          obj[header.trim()] = values[i]?.trim();
        });
        this.push(obj);
      }
    }
    callback();
  }
}

fs.createReadStream('data.csv')
  .pipe(new CSVParser())
  .on('data', (obj) => {
    console.log('Row:', obj);
  });
```

## 五、性能优化

### 1. 合理设置 highWaterMark

```javascript
const stream = fs.createReadStream('large-file.txt', {
  highWaterMark: 256 * 1024 // 256KB
});
```

### 2. 使用 pipeline 替代 pipe

```javascript
const { pipeline } = require('stream/promises');

async function copyFile(src, dest) {
  await pipeline(
    fs.createReadStream(src),
    fs.createWriteStream(dest)
  );
}
```

### 3. 背压处理

```javascript
const readStream = fs.createReadStream('large-file.txt');
const writeStream = fs.createWriteStream('output.txt');

readStream.on('data', (chunk) => {
  if (!writeStream.write(chunk)) {
    readStream.pause();
  }
});

writeStream.on('drain', () => {
  readStream.resume();
});
```

## 六、最佳实践

1. 大文件必须用流
2. 优先使用 Promise API
3. 合理处理错误
4. 使用 pipeline 处理流
5. 注意背压

## 七、总结

Node.js 文件系统与流处理：
- 掌握同步和异步 API
- 理解流的四种类型
- 善用管道和转换流
- 处理大文件用流
- 注意性能优化

掌握这些，构建高性能 Node.js 应用！
