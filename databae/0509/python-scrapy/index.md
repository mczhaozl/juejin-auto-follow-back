# Python Scrapy 爬虫完全指南

## 一、项目初始化

```bash
scrapy startproject myproject
cd myproject
scrapy genspider example example.com
```

## 二、Spider 编写

```python
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "https://quotes.toscrape.com/page/1/"
    ]
    
    def parse(self, response):
        # 提取数据
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall()
            }
        
        # 跟进下一页
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

## 三、Item Pipeline

```python
# pipelines.py
class SaveToDatabasePipeline:
    def process_item(self, item, spider):
        # 保存到数据库
        return item

# settings.py
ITEM_PIPELINES = {
    "myproject.pipelines.SaveToDatabasePipeline": 300,
}
```

## 四、Selector 使用

```python
# CSS
title = response.css("h1.title::text").get()

# XPath
title = response.xpath("//h1[@class='title']/text()").get()

# 提取属性
href = response.css("a.link::attr(href)").get()
```

## 五、最佳实践

- 遵守 robots.txt
- 使用 User-Agent 轮换
- 合理设置请求延迟
- 使用 scrapy shell 调试
- 保存中间结果和失败重试
- 考虑分布式爬取（Scrapy-Redis）
