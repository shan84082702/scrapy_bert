import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "EBC"
    allowed_domains=["news.ebc.net.tw"]
    start_urls = ['https://news.ebc.net.tw/','https://news.ebc.net.tw/news/entertainment','https://news.ebc.net.tw/news/society','https://news.ebc.net.tw/news/politics','https://news.ebc.net.tw/news/world','https://news.ebc.net.tw/news/china','https://news.ebc.net.tw/news/living','https://news.ebc.net.tw/news/business','https://news.ebc.net.tw/news/car','https://news.ebc.net.tw/news/house','https://news.ebc.net.tw/news/sport','https://news.ebc.net.tw/news/travel','https://news.ebc.net.tw/news/health']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://news.ebc.net.tw"+url
            if(url.startswith('http')):
                yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        newsItem['language']="ZH_CHT"
        newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        newsItem['crawled_at']=round(time.time()*1000)
        newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        
        
       