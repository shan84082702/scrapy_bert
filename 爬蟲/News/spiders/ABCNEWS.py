import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "ABCNEWS"
    allowed_domains=["abcnews.go.com"]
    start_urls = ['https://abcnews.go.com/', 'https://abcnews.go.com/Health/Coronavirus', 'https://abcnews.go.com/US', 'https://abcnews.go.com/Politics', 'https://abcnews.go.com/Entertainment', 'https://abcnews.go.com/International', 'https://abcnews.go.com/Business', 'https://abcnews.go.com/Technology', 'https://abcnews.go.com/Health', 'https://abcnews.go.com/Lifestyle', 'https://abcnews.go.com/Sports']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://abcnews.go.com"+url
            if(url.startswith('http')):
                yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        newsItem['language']="EN_US"
        newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        newsItem['crawled_at']=round(time.time()*1000)
        newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        
        
       