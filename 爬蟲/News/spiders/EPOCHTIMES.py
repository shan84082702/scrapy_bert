import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "EPOCHTIMES"
    allowed_domains=["epochtimes.com"]
    start_urls = ['https://news.ebc.net.tw/','https://www.epochtimes.com/b5/nsc412.htm','https://www.epochtimes.com/b5/ncid1349362.htm','https://www.epochtimes.com/b5/nsc418.htm','https://www.epochtimes.com/b5/ncid1349361.htm','https://www.epochtimes.com/b5/nsc420.htm','https://www.epochtimes.com/b5/nsc419.htm','https://www.epochtimes.com/b5/ncyule.htm','https://www.epochtimes.com/b5/nsc2008.htm','https://www.epochtimes.com/b5/nsc1002.htm','https://www.epochtimes.com/b5/nsc2007.htm']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://www.epochtimes.com/b5"+url
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
        
        
       