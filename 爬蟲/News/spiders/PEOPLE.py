import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "PEOPLE"
    allowed_domains=["people.com.cn"]
    start_urls = ['http://www.people.com.cn/BIG5/','http://politics.people.com.cn/','http://world.people.com.cn/','http://finance.people.com.cn/','http://tw.people.com.cn/','http://military.people.com.cn/','http://society.people.com.cn/','http://industry.people.com.cn/','http://edu.people.com.cn/','http://kpzg.people.com.cn/','http://culture.people.com.cn/','http://scitech.people.com.cn/','http://health.people.com.cn/','http://sports.people.com.cn/']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url=response.url.rstrip('/')+url
            if(url.startswith('http')):
                yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        #newsItem['language']="ZH_CHS" #簡體中文
        #newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        #newsItem['crawled_at']=round(time.time()*1000)
        #newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        
        
       