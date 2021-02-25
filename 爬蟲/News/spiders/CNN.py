import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "CNN"
    allowed_domains=["edition.cnn.com"]
    start_urls = ['https://edition.cnn.com/', 'https://edition.cnn.com/world', 'https://edition.cnn.com/africa', 'https://edition.cnn.com/americas', 'https://edition.cnn.com/asia', 'https://edition.cnn.com/australia', 'https://edition.cnn.com/china', 'https://edition.cnn.com/europe', 'https://edition.cnn.com/india', 'https://edition.cnn.com/middle-east', 'https://edition.cnn.com/uk', 'https://edition.cnn.com/politics', 'https://edition.cnn.com/business', 'https://edition.cnn.com/business/tech', 'https://edition.cnn.com/business/media', 'https://edition.cnn.com/business/success', 'https://edition.cnn.com/business/perspectives', 'https://edition.cnn.com/health', 'https://edition.cnn.com/specials/health/food-diet', 'https://edition.cnn.com/specials/health/fitness-excercise', 'https://edition.cnn.com/specials/health/wellness', 'https://edition.cnn.com/specials/health/parenting', 'https://edition.cnn.com/specials/health/parenting', 'https://edition.cnn.com/specials/health/vital-signs', 'https://edition.cnn.com/entertainment', 'https://edition.cnn.com/entertainment/celebrities', 'https://edition.cnn.com/entertainment/movies', 'https://edition.cnn.com/entertainment/tv-shows', 'https://edition.cnn.com/entertainment/culture', 'https://edition.cnn.com/style', 'https://edition.cnn.com/sport', 'https://edition.cnn.com/sport/football', 'https://edition.cnn.com/sport/tennis', 'https://edition.cnn.com/sport/equestrian', 'https://edition.cnn.com/sport/golf', 'https://edition.cnn.com/sport/skiing', 'https://edition.cnn.com/sport/horse-racing', 'https://edition.cnn.com/sport/motorsport', 'https://edition.cnn.com/specials/sport/formula-e', 'https://edition.cnn.com/specials/esports']
    #start_urls = ['https://edition.cnn.com/']
    
    def parse(self, response):
        #newsItem=NewsItem()
        #newsItem['contents']=response.url
        #yield newsItem
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://edition.cnn.com"+url
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
        
        
       