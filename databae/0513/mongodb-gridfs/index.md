# MongoDB GridFS 完全指南

## 一、GridFS 基础

```javascript
const { MongoClient } = require('mongodb');
const fs = require('fs');

async function main() {
  const client = new MongoClient('mongodb://localhost:27017');
  await client.connect();
  const db = client.db('mydb');
  
  // 获取 GridFS Bucket
  const bucket = new db.GridFSBucket();
  
  // 1. 上传文件
  const uploadStream = bucket.openUploadStream('large-file.pdf');
  fs.createReadStream('local-file.pdf').pipe(uploadStream);
  uploadStream.on('finish', () => console.log('Upload done'));
  
  // 2. 下载文件
  const downloadStream = bucket.openDownloadStreamByName('large-file.pdf');
  downloadStream.pipe(fs.createWriteStream('downloaded-file.pdf'));
}
```

## 二、GridFS 集合结构

```javascript
// fs.files - 文件元数据
{
  "_id": ObjectId(...),
  "length": 10485760, // 文件大小 (bytes)
  "chunkSize": 261120,
  "uploadDate": ISODate(...),
  "filename": "report.pdf",
  "md5": "abc123...",
  "metadata": {
    "author": "John",
    "category": "report"
  }
}

// fs.chunks - 文件分块
{
  "_id": ObjectId(...),
  "files_id": ObjectId(...),
  "n": 0, // 块序号
  "data": BinData(0, ...) // 二进制数据
}
```

## 三、操作方法

```javascript
// 1. 查询文件
const files = await db.collection('fs.files').find({
  filename: /\.pdf$/,
  "metadata.category": "report"
}).toArray();

// 2. 删除文件
await bucket.delete(fileId);

// 3. 流操作
const stream = bucket.openDownloadStream(fileId);
stream.on('data', (chunk) => console.log(`Received ${chunk.length} bytes`));
stream.on('end', () => console.log('Download complete'));
```

## 四、高级用法

```javascript
// 自定义 chunk size
const bucket = new db.GridFSBucket({
  chunkSizeBytes: 1024 * 1024 // 1MB chunks
});

// 重命名文件
await bucket.rename(fileId, 'new-filename.pdf');

// 文件版本控制
const versions = await db.collection('fs.files').find({
  filename: 'report.pdf'
}).sort({ uploadDate: -1 }).toArray();
```

## 最佳实践
- 大于 16MB 的文件使用 GridFS
- 合理设置 chunk size
- 利用 metadata 索引
- 考虑用对象存储替代 GridFS (S3, OSS)
- 注意备份和恢复策略
