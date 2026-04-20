# RediSearch 完全指南

## 一、创建索引

```redis
FT.CREATE myIndex 
ON HASH 
PREFIX 1 doc: 
SCHEMA 
  title TEXT 
  body TEXT 
  price NUMERIC 
  category TAG
```

## 二、添加文档

```redis
HSET doc:1 title "Redis Book" body "Learn Redis" price 29.99 category "Books"
```

## 三、查询

```redis
FT.SEARCH myIndex "Hello World"

FT.SEARCH myIndex "@title:Redis @category:{Books}"

FT.SEARCH myIndex "@price:[20 50]"

FT.AGGREGATE myIndex "*" 
  GROUPBY 1 @category 
  REDUCE COUNT 0 AS count
```

## 四、删除索引

```redis
FT.DROPINDEX myIndex
```

## 最佳实践
- 合理设计 Schema
- 使用 Stopwords 优化
- TAG 适合分类过滤
- AGGREGATE 用于分析
- 监控索引大小
