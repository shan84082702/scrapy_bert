import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "NYTIMES"
    allowed_domains=["https://www.nytimes.com/section/world"]
    start_urls = ['https://www.nytimes.com/']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://www.nytimes.com"+url
            if(url.startswith('http')):
                yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        #newsItem['language']="EN_US"
        #newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        #newsItem['crawled_at']=round(time.time()*1000)
        #newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        
        
       
        
        
       