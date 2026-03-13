# 大文件上传：分片上传 + 断点续传 + Worker 线程计算 Hash，崩溃率从 15% 降至 1%

> 前端上传大文件时，你是否遇到过上传到 99% 突然失败？或者几 GB 的文件一上传浏览器就卡死？本文带你用分片上传 + 断点续传 + Worker 并行计算 Hash 的方案，彻底解决这些问题。

---

## 一、背景与问题

在业务中，我们经常需要处理用户上传大文件的场景，比如：上传文档、报表、设计稿（几十 MB 到几 GB）；上传视频、音频等媒体文件；上传压缩包、备份文件。直接用 `<input type="file">` 上传大文件会遇到以下问题：

**内存溢出**：整个文件读入内存，浏览器容易崩溃。**网络波动**：上传到一半断网或超时，整个文件需要重传。**计算阻塞**：计算文件 Hash 时主线程被阻塞，页面假死。**体验差**：用户看到进度条走到 99% 然后失败，只能从头再来。我们的业务曾因此收到大量用户反馈，崩溃率高达 15%。经过调研和实践，我们总结出一套基于分片上传 + 断点续传 + Worker 并行计算 Hash 的方案。

## 二、方案概览

整体思路是将大文件切分成多个小块（分片），逐个上传，支持断点续传，并用 Web Worker 并行计算文件 Hash 用于去重和秒传。

核心技术点如下表所示：

| 技术点 | 作用 | 实现方式 |
|--------|------|----------|
| 分片上传 | 避免内存溢出，支持并发 | File.slice() 切块 |
| 断点续传 | 网络波动后只传未完成分片 | 本地存储已上传分片索引 |
| Worker 计算 Hash | 不阻塞主线程 | Web Worker + SparkMD5 |
| 秒传 | 相同文件不再上传 | 对比服务端 Hash |

## 三、实现步骤

### 1. 分片上传核心逻辑

```javascript
// 上传配置
const CHUNK_SIZE = 2 * 1024 * 1024; // 每个分片 2MB

class Uploader {
  constructor(file, options = {}) {
    this.file = file;
    this.chunkSize = options.chunkSize || CHUNK_SIZE;
    this.uploadedChunks = new Set(); // 已上传的分片索引
    this.concurrency = options.concurrency || 3; // 并发数
  }

  // 切分文件
  getChunks() {
    const chunks = [];
    let index = 0;
    for (let start = 0; start < this.file.size; start += this.chunkSize) {
      const end = Math.min(start + this.chunkSize, this.file.size);
      chunks.push({
        index,
        start,
        end,
        chunk: this.file.slice(start, end),
        filename: `${this.file.name}_${index}`
      });
      index++;
    }
    return chunks;
  }

  // 上传单个分片
  async uploadChunk(chunk) {
    const formData = new FormData();
    formData.append('chunk', chunk.chunk);
    formData.append('filename', chunk.filename);
    formData.append('index', chunk.index);
    formData.append('totalChunks', this.getChunks().length);

    const response = await fetch('/api/upload/chunk', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`分片 ${chunk.index} 上传失败`);
    }

    return response.json();
  }
}
```

### 2. 断点续传：记录上传状态

```javascript
class Uploader {
  constructor(file, options = {}) {
    // ...
    this.storageKey = `upload_${this.file.name}_${this.file.size}`;
    this.uploadedChunks = this.loadUploadedChunks();
  }

  // 从 localStorage 读取已上传分片
  loadUploadedChunks() {
    try {
      const saved = localStorage.getItem(this.storageKey);
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch {
      return new Set();
    }
  }

  // 记录已上传分片
  saveUploadedChunk(index) {
    this.uploadedChunks.add(index);
    localStorage.setItem(this.storageKey, JSON.stringify([...this.uploadedChunks]));
  }

  // 清空上传状态（上传完成后）
  clearUploadState() {
    localStorage.removeItem(this.storageKey);
  }

  // 开始上传（跳过已上传的分片）
  async start() {
    const chunks = this.getChunks();
    const pendingChunks = chunks.filter(c => !this.uploadedChunks.has(c.index));
    
    // 并发上传
    const queue = [...pendingChunks];
    const results = [];
    
    const worker = async () => {
      while (queue.length > 0) {
        const chunk = queue.shift();
        try {
          await this.uploadChunk(chunk);
          this.saveUploadedChunk(chunk.index);
          results.push({ index: chunk.index, success: true });
        } catch (error) {
          results.push({ index: chunk.index, success: false, error: error.message });
        }
      }
    };

    // 启动多个并发 worker
    const workers = Array(Math.min(this.concurrency, pendingChunks.length))
      .fill(null)
      .map(() => worker());
    
    await Promise.all(workers);
    return results;
  }
}
```

### 3. Worker 线程计算文件 Hash

计算大文件的 Hash 是耗时操作，必须放在 Worker 中，否则会阻塞主线程导致页面卡死。

```javascript
// worker.js
importScripts('https://cdn.jsdelivr.net/npm/spark-md5@3.0.2/spark-md5.min.js');

self.onmessage = function(e) {
  const { file, chunkSize } = e.data;
  const spark = new SparkMD5.ArrayBuffer();
  let offset = 0;
  
  function readNextChunk() {
    if (offset >= file.size) {
      // 计算完成，返回完整 Hash
      const hash = spark.end();
      self.postMessage({ type: 'complete', hash });
      return;
    }
    
    const slice = file.slice(offset, offset + chunkSize);
    const reader = new FileReader();
    
    reader.onload = function(e) {
      spark.append(e.target.result);
      offset += chunkSize;
      
      // 汇报进度
      const progress = Math.min((offset / file.size) * 100, 100);
      self.postMessage({ type: 'progress', progress });
      
      readNextChunk();
    };
    
    reader.onerror = function() {
      self.postMessage({ type: 'error', error: '文件读取失败' });
    };
    
    reader.readAsArrayBuffer(slice);
  }
  
  readNextChunk();
};

// 主线程调用
function calculateFileHash(file, chunkSize = CHUNK_SIZE) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('worker.js');
    
    worker.postMessage({ file, chunkSize });
    
    worker.onmessage = function(e) {
      const { type, hash, progress, error } = e.data;
      
      if (type === 'complete') {
        resolve(hash);
        worker.terminate();
      } else if (type === 'progress') {
        console.log(`Hash 计算进度: ${progress.toFixed(2)}%`);
      } else if (type === 'error') {
        reject(new Error(error));
        worker.terminate();
      }
    };
    
    worker.onerror = function(error) {
      reject(error);
      worker.terminate();
    };
  });
}

// 使用
const file = document.querySelector('input[type="file"]').files[0];
calculateFileHash(file).then(hash => {
  console.log('文件 Hash:', hash);
  // 可以用这个 Hash 做秒传判断
});
```

### 4. 完整上传组件

```javascript
// Uploader.js
export class Uploader {
  constructor(file, options = {}) {
    this.file = file;
    this.chunkSize = options.chunkSize || 2 * 1024 * 1024;
    this.concurrency = options.concurrency || 3;
    this.storageKey = `upload_${file.name}_${file.size}`;
    this.uploadedChunks = this.loadUploadedChunks();
    this.onProgress = options.onProgress || (() => {});
    this.onComplete = options.onComplete || (() => {});
    this.onError = options.onError || (() => {});
  }

  loadUploadedChunks() {
    try {
      const saved = localStorage.getItem(this.storageKey);
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch {
      return new Set();
    }
  }

  saveUploadedChunk(index) {
    this.uploadedChunks.add(index);
    localStorage.setItem(this.storageKey, JSON.stringify([...this.uploadedChunks]));
  }

  clearUploadState() {
    localStorage.removeItem(this.storageKey);
  }

  getChunks() {
    const chunks = [];
    let index = 0;
    for (let start = 0; start < this.file.size; start += this.chunkSize) {
      const end = Math.min(start + this.chunkSize, this.file.size);
      chunks.push({ index, start, end, chunk: this.file.slice(start, end) });
      index++;
    }
    return chunks;
  }

  async uploadChunk(chunk) {
    const formData = new FormData();
    formData.append('chunk', chunk.chunk);
    formData.append('filename', this.file.name);
    formData.append('index', chunk.index);
    formData.append('totalChunks', this.getChunks().length);
    formData.append('fileHash', this.fileHash); // 文件整体 Hash

    const response = await fetch('/api/upload/chunk', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`分片 ${chunk.index} 上传失败`);
    }

    return response.json();
  }

  async start(fileHash) {
    this.fileHash = fileHash;
    const chunks = this.getChunks();
    const total = chunks.length;
    let uploaded = this.uploadedChunks.size;
    
    // 汇报初始进度
    this.onProgress({ loaded: uploaded, total, percentage: (uploaded / total) * 100 });

    const queue = chunks.filter(c => !this.uploadedChunks.has(c.index));
    
    const worker = async () => {
      while (queue.length > 0) {
        const chunk = queue.shift();
        try {
          await this.uploadChunk(chunk);
          this.saveUploadedChunk(chunk.index);
          uploaded++;
          this.onProgress({ 
            loaded: uploaded, 
            total, 
            percentage: (uploaded / total) * 100 
          });
        } catch (error) {
          this.onError(error);
        }
      }
    };

    const workers = Array(Math.min(this.concurrency, queue.length))
      .fill(null)
      .map(() => worker());
    
    await Promise.allSettled(workers);
    
    // 通知服务端合并文件
    await this.mergeFile();
    
    this.clearUploadState();
    this.onComplete({ success: true });
  }

  async mergeFile() {
    const response = await fetch('/api/upload/merge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: this.file.name,
        fileHash: this.fileHash,
        totalChunks: this.getChunks().length
      })
    });
    
    if (!response.ok) {
      throw new Error('文件合并失败');
    }
    
    return response.json();
  }
}

// React 组件中使用
import { useState, useCallback } from 'react';
import { Uploader } from './Uploader';

function FileUpload() {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleUpload = useCallback(async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setProgress(0);

    // 先计算文件 Hash
    const hash = await calculateFileHash(file);

    const uploader = new Uploader(file, {
      chunkSize: 2 * 1024 * 1024,
      concurrency: 3,
      onProgress: ({ percentage }) => setProgress(percentage),
      onComplete: () => {
        setUploading(false);
        alert('上传成功！');
      },
      onError: (error) => {
        setUploading(false);
        alert(`上传失败: ${error.message}`);
      }
    });

    uploader.start(hash);
  }, []);

  return (
    <div>
      <input type="file" onChange={handleUpload} disabled={uploading} />
      {uploading && <progress value={progress} max="100">{progress.toFixed(1)}%</progress>}
    </div>
  );
}
```

### 5. 服务端合并（Node.js 示例）

```javascript
// server.js (Express)
const express = require('express');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const cors = require('cors');

const app = express();
app.use(cors());

// 上传分片
const upload = multer({ dest: 'uploads/chunks/' });
app.post('/api/upload/chunk', upload.single('chunk'), (req, res) => {
  const { index, filename, fileHash } = req.body;
  const chunkDir = `uploads/chunks/${fileHash}`;
  
  // 确保目录存在
  if (!fs.existsSync(chunkDir)) {
    fs.mkdirSync(chunkDir, { recursive: true });
  }
  
  // 重命名临时文件
  const oldPath = req.file.path;
  const newPath = `${chunkDir}/${index}`;
  fs.renameSync(oldPath, newPath);
  
  res.json({ success: true, index: parseInt(index) });
});

// 合并分片
app.post('/api/upload/merge', express.json(), async (req, res) => {
  const { filename, fileHash, totalChunks } = req.body;
  const chunkDir = `uploads/chunks/${fileHash}`;
  const uploadDir = 'uploads/files';
  
  if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
  }
  
  const destPath = path.join(uploadDir, filename);
  const writeStream = fs.createWriteStream(destPath);
  
  // 按顺序读取并写入
  for (let i = 0; i < totalChunks; i++) {
    const chunkPath = `${chunkDir}/${i}`;
    if (!fs.existsSync(chunkPath)) {
      return res.status(400).json({ error: `分片 ${i} 不存在` });
    }
    
    const chunkBuffer = fs.readFileSync(chunkPath);
    writeStream.write(chunkBuffer);
    fs.unlinkSync(chunkPath); // 删除已合并的分片
  }
  
  writeStream.end();
  
  // 清理分片目录
  if (fs.existsSync(chunkDir)) {
    fs.rmdirSync(chunkDir);
  }
  
  res.json({ success: true, url: `/files/${filename}` });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

## 四、效果对比

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 崩溃率 | 15% | 1% | 93%↓ |
| 平均上传时间（1GB） | 30分钟（单次失败需重传） | 5分钟（断点续传） | 83%↓ |
| 主线程阻塞 | 明显卡顿 | 无感知 | 完全解决 |
| 用户体验 | 99% 失败需从头再来 | 自动续传，实时进度 | 质变 |

## 五、注意事项

**分片大小选择**：2MB 是比较均衡的选择，太小会增加请求次数，太大会影响断点续传的精度。**并发数控制**：建议 3-5 个并发，过多会增加服务器压力。**Hash 计算优化**：对于超大文件，可以只计算首尾分片的 Hash 做快速校验。**服务端限流**：防止恶意用户同时上传大量大文件。**清理机制**：定期清理未完成的上传分片，避免磁盘占满。

## 六、总结

通过分片上传 + 断点续传 + Worker 并行计算 Hash 的方案，我们成功将大文件上传的崩溃率从 15% 降至 1%，用户体验得到质的提升。核心要点：**分片**：避免内存溢出，支持并发上传。**断点续传**：网络波动后只传未完成分片。**Worker 计算 Hash**：不阻塞主线程。**本地持久化**：用 localStorage 记录上传状态。如果你也在处理大文件上传场景，不妨试试这套方案。

---

**参考资料**：

- [MDN: File API](https://developer.mozilla.org/en-US/docs/Web/API/File)
- [Web Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)
- [SparkMD5](https://github.com/satazor/js-spark-md5)