import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "CDNS"
    allowed_domains=["cdns.com.tw"]
    start_urls = ['https://www.cdns.com.tw/','https://www.cdns.com.tw/index/taiwan_tc','https://www.cdns.com.tw/index/tainan_tc','https://www.cdns.com.tw/index/local','https://www.cdns.com.tw/index/live_tc','https://www.cdns.com.tw/index/view','https://www.cdns.com.tw/index/society','https://www.cdns.com.tw/index/health_tc','https://www.cdns.com.tw/index/culture_tc','https://www.cdns.com.tw/index/international_tc']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url='https://www.cdns.com.tw'+url
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
        
        
       