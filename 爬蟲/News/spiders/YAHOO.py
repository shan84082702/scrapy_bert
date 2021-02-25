import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "YAHOO"
    allowed_domains=["tw.news.yahoo.com/"]
    start_urls = ['https://tw.news.yahoo.com/politics']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://tw.news.yahoo.com"+url
            if(url.startswith('http')):
                yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        #newsItem['language']="ZH_CHT"
        #newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        #newsItem['crawled_at']=round(time.time()*1000)
        #newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        
        
       