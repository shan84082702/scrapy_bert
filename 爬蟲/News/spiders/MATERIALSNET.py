import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "MATERIALSNET"
    allowed_domains=["www.materialsnet.com.tw"]
    start_urls = ['https://www.materialsnet.com.tw/','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=45&atttype=1','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=152&atttype=1','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=27&atttype=1','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=287&atttype=1','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=300&atttype=1','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=296&atttype=1','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=291&atttype=1','https://www.materialsnet.com.tw/DocSearch1.aspx?attid=28&atttype=1','https://www.materialsnet.com.tw/material/MaterialFront.aspx','https://www.materialsnet.com.tw/material/MaterialNews.aspx','https://www.materialsnet.com.tw/material/MaterialTopic.aspx','https://www.materialsnet.com.tw/tech/TechSearch.aspx','https://www.materialsnet.com.tw/tech/TechExpert.aspx','https://www.materialsnet.com.tw/tech/TechNew.aspx','https://www.materialsnet.com.tw/tech/TechPoint.aspx','https://www.materialsnet.com.tw/tech/TechMove.aspx','https://www.materialsnet.com.tw/tech/TechService.aspx']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://www.materialsnet.com.tw"+url
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
        
        
       