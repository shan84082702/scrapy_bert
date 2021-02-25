import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "CHINA"
    allowed_domains=["china.com"]
    start_urls = ['https://news.china.com/','https://news.china.com/domestic/index.html','https://news.china.com/international/index.html','https://news.china.com/social/index.html','https://finance.china.com/','https://news.china.com/zw/','https://military.china.com/news','https://military.china.com/global','https://military.china.com/topic','https://military.china.com/history','https://military.china.com/jxkt','https://military.china.com/aerospace','https://ent.china.com/','https://ent.china.com/star/news/','https://ent.china.com/movie/','https://ent.china.com/tv/','https://ent.china.com/music/top/','https://health.china.com/']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url='https://military.china.com'+url
            if(url.startswith('http')):
                yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        newsItem['language']="ZH_CHS" #簡體中文
        newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        newsItem['crawled_at']=round(time.time()*1000)
        newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        
        
       